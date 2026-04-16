"""Simple pygame animation of wandering squares that flee larger neighbors."""

import random
import sys
from typing import Sequence

import pygame



# Window and animation settings.
WIDTH = 800
HEIGHT = 600
FPS = 60
SQUARE_COUNT = 30
SQUARE_SIZE = 30
SQUARE_SIZE_MAX=60
SQUARE_SIZE_MIN=10
MAX_SPEED = 15
VELOCITY_CHANGE_CHANCE = 0.03
Color = tuple[int, int, int]

MIN_LIFESPAN:int=5
MAX_LIFESPAN:int=20
ROUNDOFF:float=0.1
CELL_SIZE: int = 100 
FLEE_RADIUS: float = 60 

class Square:
	"""Represents one moving square on the screen."""

	def __init__(self) -> None:
		"""Initialize randomized motion, color, and lifespan metadata."""
		# Start at a random position with a random speed and color.
		self.size: int = random.randint(SQUARE_SIZE_MIN, SQUARE_SIZE_MAX)
		self.x: float = random.randint(0, WIDTH - self.size)
		self.y: float = random.randint(0, HEIGHT - self.size)
		self.vx: float = MAX_SPEED / self.size
		self.vy: float = self.vx
		self.color: Color = (
			random.randint(50, 255),
			random.randint(50, 255),
			random.randint(50, 255),
		)
		self.lifespan: int = random.randint(MIN_LIFESPAN, MAX_LIFESPAN)
		self.birth_time: float = pygame.time.get_ticks() / 1000
		self.remaining_life: float = float(self.lifespan)
		self.alive: bool = True

	def update(self, squares: Sequence["Square"]) -> None:
		"""Advance movement, bounce at edges, flee threats, and age the square."""
		# Sometimes slightly change direction to look more random.
		if random.random() < VELOCITY_CHANGE_CHANCE:
			self.vx += random.choice([-1, 0, 1]) * (self.size / SQUARE_SIZE_MAX)
			self.vy += random.choice([-1, 0, 1]) * (self.size / SQUARE_SIZE_MAX)

			# Keep speed inside allowed limits.
			self.vx = max(-MAX_SPEED, min(MAX_SPEED, self.vx))
			self.vy = max(-MAX_SPEED, min(MAX_SPEED, self.vy))

			# Avoid fully stopping a square.
			if self.vx == 0:
				self.vx = random.choice([-1, 1])
			if self.vy == 0:
				self.vy = random.choice([-1, 1])

		# Move square based on current speed.
		self.x += self.vx
		self.y += self.vy

		# Bounce horizontally when touching left/right edges.
		if self.x < 0:
			self.x = 0
			self.vx *= -1
		elif self.x + self.size > WIDTH:
			self.x = WIDTH - self.size
			self.vx *= -1

		# Bounce vertically when touching top/bottom edges.
		if self.y < 0:
			self.y = 0
			self.vy *= -1
		elif self.y + self.size > HEIGHT:
			self.y = HEIGHT - self.size
			self.vy *= -1
		
		# Flee from nearby larger threats using spatial grid partitioning (O(k) vs O(n²)).		
		# Build spatial grid: map cell coordinates to list of squares in that cell.
		grid: dict[tuple[int, int], list[Square]] = {}
		for square in squares:
			# Determine which grid cells this square occupies (handles variable sizes).
			cell_x_min: int = int(square.x // CELL_SIZE)
			cell_x_max: int = int((square.x + square.size) // CELL_SIZE)
			cell_y_min: int = int(square.y // CELL_SIZE)
			cell_y_max: int = int((square.y + square.size) // CELL_SIZE)

			# Store square in all cells it occupies for neighbor discovery.
			for cx in range(cell_x_min, cell_x_max + 1):
				for cy in range(cell_y_min, cell_y_max + 1):
					if (cx, cy) not in grid:
						grid[(cx, cy)] = []
					grid[(cx, cy)].append(square)
		
		# Query neighboring grid cells (3×3 neighborhood) for threats.
		my_cell_x: int = int(self.x // CELL_SIZE)
		my_cell_y: int = int(self.y // CELL_SIZE)
		
		for cx in range(my_cell_x - 1, my_cell_x + 2):
			for cy in range(my_cell_y - 1, my_cell_y + 2):
				if (cx, cy) not in grid:
					continue
				
				for threat in grid[(cx, cy)]:
					# Skip self-comparison.
					if threat is self:
						continue
					
					# Calculate displacement vector from self center to threat center.
					dx: float = (threat.x + threat.size / 2) - (self.x + self.size / 2)
					dy: float = (threat.y + threat.size / 2) - (self.y + self.size / 2)
					distance: float = (dx * dx + dy * dy) ** 0.5
					
					# Flee if threat is larger and within flee radius.
					if 0 < distance < FLEE_RADIUS and self.size < threat.size:
						# Separate direction and speed for stable, predictable fleeing.
						
						# 1. Calculate current speed (magnitude of velocity vector).
						current_speed: float = (self.vx * self.vx + self.vy * self.vy) ** 0.5
						
						# 2. Normalize flee direction (unit vector pointing away from threat).
						flee_dir_x: float = -dx / distance  # Negative dx/distance points away
						flee_dir_y: float = -dy / distance
						
						# 3. Apply speed to normalized direction for stable fleeing velocity.
						self.vx = current_speed * flee_dir_x
						self.vy = current_speed * flee_dir_y
		
		# To update the remaining_life
		current_time: float = pygame.time.get_ticks() / 1000
		self.remaining_life = self.lifespan - (current_time - self.birth_time)
		if self.remaining_life < ROUNDOFF:
			self.alive = False


	def draw(self, surface: pygame.Surface) -> None:
		"""Draw the square with a slight jitter for a hand-drawn effect."""
		x = self.x + (random.choice([1, -1]) * (self.size / SQUARE_SIZE_MAX * 1))
		y = self.y + (random.choice([1, -1]) * (self.size / SQUARE_SIZE_MAX * 1))
		pygame.draw.rect(surface, self.color, (x, y, self.size, self.size))


def main() -> None:
	"""Run the game loop: input, update, draw, repeat."""

	# 1) Start pygame and create window objects.
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Random Moving Squares")
	clock = pygame.time.Clock()

	# 2) Create 10 square objects.
	squares: list[Square] = [Square() for _ in range(SQUARE_COUNT)]

	# 3) Main loop: handle events, update state, draw frame.
	running: bool = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		for square in squares:
			square.update(squares)
			
		squares=[square if square.alive else Square() for square in squares]
		screen.fill((18, 18, 24))
		for square in squares:
			square.draw(screen)

		pygame.display.flip()
		clock.tick(FPS)

	# 4) Clean shutdown.
	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
