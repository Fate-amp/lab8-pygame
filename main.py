"""Predator-prey simulation with time-based physics and spatial grid optimization.

This module implements a pygame-based animation featuring multiple colored squares
that exhibit fleeing and chasing behaviors based on relative size. Larger squares
chase smaller ones, while smaller squares flee from larger threats.

Key features:
- Time-based physics: all movement scaled by delta time for framerate-independent behavior.
- Spatial grid partitioning for O(k) neighbor lookup instead of O(n²).
- Velocity-based steering with normalized direction vectors for stable movement.
- Size-based predator/prey relationships with configurable radii.
- Lifespan-based square renewal for continuous simulation.
"""

import random
import sys

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
BIG_SQUARE_COUNT:int=5
MEDIUM_SQUARE_COUNT:int=10
SMALL_SQUARE_COUNT:int=30
BIG_SQUARE_SIZE:int=25
MEDIUM_SQUARE_SIZE:int=10
SMALL_SQUARE_SIZE:int=4
SQUARE_SIZE_MAX: int = 60  # Maximum square side length in pixels.
SQUARE_SIZE_MIN: int = 10  # Minimum square side length in pixels.
MAX_SPEED: float = 200  # Maximum velocity magnitude (pixels per second).
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


TRAILS_LENGTH = 30
TEST_MODE_ON : bool = True
GROWTH_SPEED:int=500 #unit:ms
class Square:
	"""Represents one moving square in the predator-prey simulation.
	
	Each square has a size, position, velocity, color, and lifespan. Squares interact
	via fleeing and chasing behaviors based on their relative sizes and proximity.
	Larger squares chase smaller ones; smaller squares flee from larger ones.
	"""

	def __init__(self,size) -> None:
		"""Initialize a new square with random attributes.
		
		Randomly assigns:
		- size: uniformly from [SQUARE_SIZE_MIN, SQUARE_SIZE_MAX]
		- position: uniformly within the window bounds
		- color: random RGB tuple
		- initial velocity: random direction with speed inversely proportional to size (pixels/second)
		- lifespan: uniformly from [MIN_LIFESPAN, MAX_LIFESPAN]
		
		Attributes:
			size (int): Side length of the square in pixels.
			x (float): X-coordinate of top-left corner.
			y (float): Y-coordinate of top-left corner.
			vx (float): Velocity in X direction (pixels per second).
			vy (float): Velocity in Y direction (pixels per second).
			color (Color): RGB tuple for rendering.
			lifespan (int): Total lifespan in seconds.
			birth_time (float): Timestamp when square was created (seconds since program start).
			remaining_life (float): Remaining lifespan (seconds).
			alive (bool): Whether square is still active in simulation.
		"""
		# Start at a random position with a random speed and color.
		self.size: int = size
		self.x: float = random.randint(0, WIDTH - self.size)
		self.y: float = random.randint(0, HEIGHT - self.size)
		# Random direction with speed proportional to size (pixels/second).
		angle: float = random.uniform(0, 2 * 3.14159)
		speed: float = MAX_SPEED / self.size
		self.vx = speed * (angle ** 0.5)
		self.vy = speed * ((2 * 3.14159 - angle) ** 0.5)
		self.color: Color = (
			random.randint(50, 255),
			random.randint(50, 255),
			random.randint(50, 255),
		)
		self.lifespan: int = random.randint(MIN_LIFESPAN, MAX_LIFESPAN)
		self.birth_time: float = pygame.time.get_ticks() / 1000
		self.remaining_life: float = float(self.lifespan)
		self.alive: bool = True
		self.test_initial_x=self.x
		self.test_initial_y=self.y
		test_vx=None
		test_vy=None

	def update(self, dt: float) -> None:
		"""Update square state: apply random perturbation, move, handle collisions, and age.
		
		Time-based physics update ensures consistent motion regardless of framerate:
		1. Apply random velocity perturbation (VELOCITY_CHANGE_CHANCE probability).
		2. Move position: new_pos = old_pos + velocity × dt (pixel-accurate).
		3. Handle wall bounces by reversing velocity component.
		4. Update lifespan and mark dead if expired.
		
		Note: Flee/chase steering applied separately in main() via find_threat_or_prey().
		
		Args:
			dt: Delta time in seconds since last frame.
		
		Complexity: O(1) per square update.
		"""
		# Sometimes slightly change direction to look more random.
		if random.random() < VELOCITY_CHANGE_CHANCE:
			# Add small perturbation proportional to size (smaller = more agile).
			perturbation: float = 50 * (self.size / SQUARE_SIZE_MAX)  # pixels/second
			self.vx += random.choice([-1, 0, 1]) * perturbation
			self.vy += random.choice([-1, 0, 1]) * perturbation

			# Keep speed inside allowed limits.
			self.vx = max(-MAX_SPEED, min(MAX_SPEED, self.vx))
			self.vy = max(-MAX_SPEED, min(MAX_SPEED, self.vy))

			# Avoid fully stopping a square.
			if self.vx == 0:
				self.vx = random.choice([-50, 50])
			if self.vy == 0:
				self.vy = random.choice([-50, 50])

		# Move square based on current speed.
		self.x += self.vx*dt
		self.y += self.vy*dt

		# Wrap horizontally when touching left/right edges.
		if self.x < 0:
			self.x = WIDTH - self.size
			self.x=max(0,min(self.x,WIDTH-self.size))
		elif self.x + self.size > WIDTH:
			self.x = 0
			self.x=max(0,min(self.x,WIDTH-self.size))

		# Wrap vertically when touching top/bottom edges.
		if self.y < 0:
			self.y = HEIGHT - self.size
			self.y=max(0,min(self.y,HEIGHT-self.size))
		elif self.y + self.size > HEIGHT:
			self.y=0
			self.y=max(0,min(self.y,HEIGHT-self.size))

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
		pygame.draw.line(surface,self.color,start_pos=(self.x,self.y),end_pos=(self.x-TRAILS_LENGTH,self.y-TRAILS_LENGTH))
	def check_collision(self, other:Square) -> bool:
		rect1=pygame.Rect(self.x,self.y,self.size,self.size)
		rect2=pygame.Rect(other.x,other.y,other.size,other.size)
		return rect1.colliderect(rect2)

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

def find_collisions_in_grid(square,grid,dt):
	cell_x: int = int(square.x // CELL_SIZE)
	cell_y: int = int(square.y // CELL_SIZE)
	neighbor_cell: tuple[int, int] = (cell_x, cell_y)
	for neighbor in grid.get(neighbor_cell, []):
		if neighbor is square:
				continue
		if square.check_collision(neighbor) and square.size>neighbor.size:
			square.size+=(neighbor.size*dt)/GROWTH_SPEED
			neighbor.alive=False

def main() -> None:
	"""Initialize pygame and run the main game loop with time-based physics.
	
	Steps:
	1. Initialize pygame and create a windowed display.
	2. Create SQUARE_COUNT square objects with random initial states.
	3. Main event loop (time-based):
	   - Measure delta time since last frame.
	   - Process pygame events (quit on window close).
	   - Update all squares' positions using time-based physics (velocity × dt).
	   - Apply flee/chase behaviors based on spatial grid neighbors.
	   - Remove expired squares and replace with new ones.
	   - Render all squares.
	   - Maintain target FPS using clock.tick().
	4. Gracefully shut down pygame and exit.
	
	Time-based physics ensures consistent motion regardless of framerate.
	"""

	# 1) Start pygame and create window objects.
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Random Moving Squares")
	clock = pygame.time.Clock()

	# 2) Create initial squares.
	squares: list[Square] = []
	for _ in range(BIG_SQUARE_COUNT):
		squares.append(Square(BIG_SQUARE_SIZE))
	for _ in range(MEDIUM_SQUARE_COUNT):
		squares.append(Square(MEDIUM_SQUARE_SIZE))
	for _ in range(SMALL_SQUARE_COUNT):
		squares.append(Square(SMALL_SQUARE_SIZE))

	# 3) Main loop: handle events, update state, draw frame.
	running: bool = True
	while running:
		dt: float = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds.
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			
		for square in squares:
			square.update(dt)
		
		if TEST_MODE_ON:
			for square in squares:
				dx=square.x-square.test_initial_x
				square.test_vx=dx/dt
				dy=square.y-square.test_initial_y
				square.test_vy=dy/dt
			print(all(square.vx==square.test_vx and square.vy==square.test_vy))

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
		find_collisions_in_grid(square,grid,dt)
		# To update the squares list based on the size
		dead_squares_big=0
		dead_squares_medium=0
		dead_squares_small=0
		if not square.alive and square.size==BIG_SQUARE_SIZE:
			dead_squares_big+=1
		if not square.alive and square.size==MEDIUM_SQUARE_SIZE:
			dead_squares_medium+=1
		if not square.alive and square.size==SMALL_SQUARE_SIZE:
			dead_squares_small+=1
		survivors=[]
		for square in squares:
			if square.alive:
				survivors.append(square)
		for _ in range(dead_squares_big):
			survivors.append(Square(BIG_SQUARE_SIZE))
		for _ in range(dead_squares_medium):
			survivors.append(Square(MEDIUM_SQUARE_SIZE))
		for _ in range(dead_squares_small):
			survivors.append(Square(SMALL_SQUARE_SIZE))
		squares=survivors
		screen.fill((18, 18, 24))
		for square in squares:
			square.draw(screen)

		pygame.display.flip()

	# 4) Clean shutdown.
	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
