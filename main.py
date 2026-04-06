import random
import sys

import pygame



# Window and animation settings.
WIDTH = 800
HEIGHT = 600
FPS = 60
SQUARE_COUNT = 100
SQUARE_SIZE = 30
SQUARE_SIZE_MAX=60
SQUARE_SIZE_MIN=30
MAX_SPEED = 15
VELOCITY_CHANGE_CHANCE = 0.03


class Square:
	"""Represents one moving square on the screen."""

	def __init__(self) -> None:
		# Start at a random position with a random speed and color.
		self.size = random.randint(SQUARE_SIZE_MIN,SQUARE_SIZE_MAX)
		self.x = random.randint(0, WIDTH - self.size)
		self.y = random.randint(0, HEIGHT - self.size)
		self.vx = MAX_SPEED/self.size
		self.vy = self.vx
		self.color = (
			random.randint(50, 255),
			random.randint(50, 255),
			random.randint(50, 255),
		)

	def update(self) -> None:
		# Sometimes slightly change direction to look more random.
		if random.random() < VELOCITY_CHANGE_CHANCE:
			# self.vx += random.choice([-1, 0, 1])*(self.size/SQUARE_SIZE_MAX)
			# self.vy += random.choice([-1, 0, 1])*(self.size/SQUARE_SIZE_MAX)

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

	def draw(self, surface: pygame.Surface) -> None:
		pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))


def main() -> None:
	"""Run the game loop: input, update, draw, repeat."""

	# 1) Start pygame and create window objects.
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Random Moving Squares")
	clock = pygame.time.Clock()

	# 2) Create 10 square objects.
	squares = [Square() for _ in range(SQUARE_COUNT)]

	# 3) Main loop: handle events, update state, draw frame.
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		for square in squares:
			square.update()

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
