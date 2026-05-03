"""Predator-prey simulation with spatial grid optimization.

This module implements a pygame-based animation featuring multiple colored squares
that exhibit fleeing and chasing behaviors based on relative size. Larger squares
chase smaller ones, while smaller squares flee from larger threats.

Key features:
- Spatial grid partitioning for O(k) neighbor lookup instead of O(n²).
- Velocity-based steering with normalized direction vectors for stable movement.
- Size-based predator/prey relationships with configurable radii.
- Lifespan-based square renewal for continuous simulation.
"""

import random
import sys
from typing import Sequence

import pygame


# ============================================================================
# WINDOW AND DISPLAY SETTINGS
# ============================================================================
WIDTH: int = 800  # Pixel width of game window.
HEIGHT: int = 600  # Pixel height of game window.
FPS: int = 60  # Target frames per second.

# ============================================================================
# SQUARE SIMULATION SETTINGS
# ============================================================================
SQUARE_COUNT: int = 5  # Number of squares in the simulation.
SQUARE_SIZE: int = 30  # Default square size (unused; random per-square).
SQUARE_SIZE_MAX: int = 60  # Maximum square side length in pixels.
SQUARE_SIZE_MIN: int = 10  # Minimum square side length in pixels.
MAX_SPEED: float = 30  # Maximum velocity magnitude (pixels per frame).
VELOCITY_CHANGE_CHANCE: float = 0.03  # Probability per frame of random direction change.

# ============================================================================
# COLOR AND LIFESPAN SETTINGS
# ============================================================================
Color = tuple[int, int, int]  # RGB color type alias.
MIN_LIFESPAN: int = 5  # Minimum lifespan in seconds before square expires.
MAX_LIFESPAN: int = 20  # Maximum lifespan in seconds before square expires.
ROUNDOFF: float = 0.1  # Threshold for lifespan expiration (seconds).

# ============================================================================
# SPATIAL GRID AND BEHAVIOR SETTINGS
# ============================================================================
CELL_SIZE: int = 100  # Grid cell size in pixels for neighbor partitioning.
FLEE_RADIUS: float = 50  # Distance (pixels) at which smaller squares detect and flee from larger threats.
CHASE_RADIUS: float = 80  # Distance (pixels) at which larger squares detect and chase smaller prey.
CHASE_STRENGTH: float = 0.2  # Blending factor (0.0-1.0) controlling predator steering intensity; higher = more aggressive steering.

class Square:
	"""Represents one moving square in the predator-prey simulation.
	
	Each square has a size, position, velocity, color, and lifespan. Squares interact
	via fleeing and chasing behaviors based on their relative sizes and proximity.
	Larger squares chase smaller ones; smaller squares flee from larger ones.
	"""

	def __init__(self) -> None:
		"""Initialize a new square with random attributes.
		
		Randomly assigns:
		- size: uniformly from [SQUARE_SIZE_MIN, SQUARE_SIZE_MAX]
		- position: uniformly within the window bounds
		- color: random RGB tuple
		- initial velocity: inversely proportional to size for gameplay balance
		- lifespan: uniformly from [MIN_LIFESPAN, MAX_LIFESPAN]
		
		Attributes:
			size (int): Side length of the square in pixels.
			x (float): X-coordinate of top-left corner.
			y (float): Y-coordinate of top-left corner.
			vx (float): Velocity in X direction (pixels per frame).
			vy (float): Velocity in Y direction (pixels per frame).
			color (Color): RGB tuple for rendering.
			lifespan (int): Total lifespan in seconds.
			birth_time (float): Timestamp when square was created (seconds since program start).
			remaining_life (float): Remaining lifespan (seconds).
			alive (bool): Whether square is still active in simulation.
		"""
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

	def update(self) -> None:
		"""Update square state for one frame: random movement, position, and aging.
		
		Performs per-frame updates independent of other squares:
		1. Apply random velocity perturbation (VELOCITY_CHANGE_CHANCE probability).
		2. Advance position based on current velocity.
		3. Bounce off window edges (invert velocity component).
		4. Update remaining lifespan and mark dead if expired.
		
		Note: Flee/chase steering is applied separately in main() using find_threat_or_prey().
		
		Complexity: O(1) per square update.
		"""
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

		# To update the remaining_life
		current_time: float = pygame.time.get_ticks() / 1000
		self.remaining_life = self.lifespan - (current_time - self.birth_time)
		if self.remaining_life < ROUNDOFF:
			self.alive = False

	def draw(self, surface: pygame.Surface) -> None:
		"""Render the square to the given surface with visual jitter.
		
		Adds random pixel offsets (±1 scaled by size) to create a hand-drawn,
		slightly wobbly appearance on each render.
		
		Args:
			surface: pygame.Surface to draw onto (typically the screen).
		"""
		x = self.x + (random.choice([1, -1]) * (self.size / SQUARE_SIZE_MAX * 1))
		y = self.y + (random.choice([1, -1]) * (self.size / SQUARE_SIZE_MAX * 1))
		pygame.draw.rect(surface, self.color, (x, y, self.size, self.size))
def find_threat_or_prey(
	square: Square,
	grid: dict[tuple[int, int], list[Square]],
) -> tuple[Square | None, Square | None]:
	"""Find the closest threat (larger square) and prey (smaller square) using spatial grid.
	
	Searches the 3×3 neighborhood of grid cells around the square's current position.
	Returns the closest larger square within FLEE_RADIUS (threat) and closest smaller
	square within CHASE_RADIUS (prey).
	
	Args:
		square: The square to find threats and prey for.
		grid: Spatial grid mapping cell coordinates to lists of squares.
	
	Returns:
		Tuple of (closest_threat, closest_prey), either can be None if not found.
	"""
	closest_threat: Square | None = None
	closest_threat_dist: float = float('inf')
	closest_prey: Square | None = None
	closest_prey_dist: float = float('inf')
	cell_x: int = int(square.x // CELL_SIZE)
	cell_y: int = int(square.y // CELL_SIZE)
	for dx in [-1, 0, 1]:
		for dy in [-1, 0, 1]:
			neighbor_cell: tuple[int, int] = (cell_x + dx, cell_y + dy)
			for neighbor in grid.get(neighbor_cell, []):
				if neighbor is square:
					continue
				# Calculate distance between square centers.
				dx_dist: float = square.x - neighbor.x
				dy_dist: float = square.y - neighbor.y
				dist: float = (dx_dist ** 2 + dy_dist ** 2) ** 0.5
				# Track threat if neighbor is bigger and within FLEE_RADIUS.
				if neighbor.size > square.size and dist < FLEE_RADIUS:
					if dist < closest_threat_dist:
						closest_threat = neighbor
						closest_threat_dist = dist
				# Track prey if neighbor is smaller and within CHASE_RADIUS.
				elif neighbor.size < square.size and dist < CHASE_RADIUS:
					if dist < closest_prey_dist:
						closest_prey = neighbor
						closest_prey_dist = dist
	return closest_threat, closest_prey


def main() -> None:
	"""Initialize pygame and run the main game loop.
	
	Steps:
	1. Initialize pygame and create a windowed display.
	2. Create SQUARE_COUNT square objects with random initial states.
	3. Main event loop:
	   - Process pygame events (quit on window close).
	   - Update all squares' positions and behaviors.
	   - Remove expired squares and replace with new ones.
	   - Clear screen and render all squares.
	   - Display and tick clock to maintain target FPS.
	4. Gracefully shut down pygame and exit.
	
	This loop runs until the user closes the window or presses quit.
	"""

	# 1) Start pygame and create window objects.
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Random Moving Squares")
	clock = pygame.time.Clock()

	# 2) Create initial squares.
	squares: list[Square] = [Square() for _ in range(SQUARE_COUNT)]

	# 3) Main loop: handle events, update state, draw frame.
	running: bool = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		for square in squares:
			square.update()

		squares = [square if square.alive else Square() for square in squares]

		# Build grid for neighbor lookup
		grid: dict[tuple[int, int], list[Square]] = {}
		for square in squares:
			cell_x_min: int = int(square.x // CELL_SIZE)
			cell_x_max: int = int((square.x + square.size) // CELL_SIZE)
			cell_y_min: int = int(square.y // CELL_SIZE)
			cell_y_max: int = int((square.y + square.size) // CELL_SIZE)

			for cx in range(cell_x_min, cell_x_max + 1):
				for cy in range(cell_y_min, cell_y_max + 1):
					if (cx, cy) not in grid:
						grid[(cx, cy)] = []
					grid[(cx, cy)].append(square)


		# Apply flee/chase steering to each square based on grid neighbors.
		for square in squares:
			threat, prey = find_threat_or_prey(square, grid)
			speed: float = (square.vx ** 2 + square.vy ** 2) ** 0.5 or 1
			if threat:
				# Flee: move away from threat.
				dx: float = square.x - threat.x
				dy: float = square.y - threat.y
				dist: float = (dx ** 2 + dy ** 2) ** 0.5 or 1
				square.vx = (dx / dist) * speed
				square.vy = (dy / dist) * speed
			elif prey:
				# Chase: move toward prey.
				dx = prey.x - square.x
				dy = prey.y - square.y
				dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
				square.vx = (dx / dist) * speed
				square.vy = (dy / dist) * speed

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
