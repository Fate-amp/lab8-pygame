# JavaScript Port Plan: Predator-Prey Simulation

**Target Deliverable:** `web/index.html` (single, self-contained file)  
**Strategy:** 1-to-1 structural mapping with no refactoring or logic improvements.

---

## Table of Contents
1. [Overview](#overview)
2. [Global Configuration Constants](#global-configuration-constants)
3. [Data Structures & Classes](#data-structures--classes)
4. [Key Functions](#key-functions)
5. [Main Simulation Loop](#main-simulation-loop)
6. [Canvas Graphics Translation](#canvas-graphics-translation)
7. [Event Handling](#event-handling)
8. [Time Management (dt Calculation)](#time-management-dt-calculation)
9. [Implementation Checklist](#implementation-checklist)

---

## Overview

The Python application is a **time-based predator-prey simulation** where colored squares interact based on size relationships:
- **Larger squares chase smaller ones** (within CHASE_RADIUS)
- **Smaller squares flee from larger ones** (within FLEE_RADIUS)
- Squares wrap at screen edges, have random velocity perturbations, and expire after a lifespan
- Spatial grid partitioning (O(k) neighbor lookup) for efficient collision detection

### Pygame-to-Canvas Translation Map

| Pygame Concept | JavaScript Equivalent |
|---|---|
| `pygame.init()` | Canvas initialization (no direct equivalent) |
| `pygame.display.set_mode()` | Create `<canvas>` element |
| `pygame.display.set_caption()` | Set `<title>` tag |
| `clock.tick(FPS)` | `requestAnimationFrame()` with dt calculation |
| `pygame.event.get()` | `addEventListener('keydown', 'keyup', 'mousemove', etc.)` |
| `pygame.display.flip()` | Frame already rendered to canvas (no explicit call needed) |
| `pygame.draw.rect()` | `ctx.fillRect()` or `ctx.strokeRect()` |
| `pygame.draw.line()` | `ctx.strokeLine()` or `ctx.lineTo()` + `ctx.stroke()` |
| `screen.fill()` | `ctx.fillStyle` + `ctx.fillRect()` for entire canvas |

---

## Global Configuration Constants

### Translation Strategy
Create a JavaScript object `CONFIG` at the top of the `<script>` block that mirrors all Python constants. Use `const` for values that never change.

```javascript
// Equivalent to: WIDTH = 800, HEIGHT = 600, FPS = 60, etc.
const CONFIG = {
  WIDTH: 800,
  HEIGHT: 600,
  FPS: 60,
  
  // Square counts and sizes
  BIG_SQUARE_COUNT: 5,
  MEDIUM_SQUARE_COUNT: 10,
  SMALL_SQUARE_COUNT: 30,
  BIG_SQUARE_SIZE: 25,
  MEDIUM_SQUARE_SIZE: 10,
  SMALL_SQUARE_SIZE: 4,
  SQUARE_SIZE_MAX: 60,
  SQUARE_SIZE_MIN: 10,
  MAX_SPEED: 200,
  VELOCITY_CHANGE_CHANCE: 0.03,
  
  // Lifespan and behavior
  MIN_LIFESPAN: 5,
  MAX_LIFESPAN: 20,
  ROUNDOFF: 0.1,
  
  // Grid and steering
  CELL_SIZE: 100,
  FLEE_RADIUS: 50,
  CHASE_RADIUS: 80,
  CHASE_STRENGTH: 0.2,
  
  // Visual effects
  TRAILS_LENGTH: 30,
  TEST_MODE_ON: true,
  GROWTH_SPEED: 500, // milliseconds
  
  // Canvas background color (RGB)
  BG_COLOR: { r: 18, g: 18, b: 24 }
};
```

### Color Type Alias
Python uses `Color = tuple[int, int, int]`. In JavaScript, use objects:
```javascript
// Example color object
const color = { r: 255, g: 0, b: 0 }; // Red
```

---

## Data Structures & Classes

### Square Class

**Python Structure:**
```python
class Square:
    def __init__(self, size):
        self.size, self.x, self.y, self.vx, self.vy, self.color, 
        self.lifespan, self.birth_time, self.remaining_life, self.alive
```

**JavaScript Translation:**
```javascript
class Square {
  constructor(size) {
    // Initialize exactly as Python does (same order, same logic)
    this.size = size;
    this.x = Math.random() * (CONFIG.WIDTH - this.size);
    this.y = Math.random() * (CONFIG.HEIGHT - this.size);
    
    // Random direction with speed inversely proportional to size
    const angle = Math.random() * 2 * Math.PI;
    const speed = CONFIG.MAX_SPEED / this.size;
    this.vx = speed * Math.sqrt(angle);
    this.vy = speed * Math.sqrt(2 * Math.PI - angle);
    
    // Random RGB color
    this.color = {
      r: Math.floor(Math.random() * 206) + 50,  // 50-255
      g: Math.floor(Math.random() * 206) + 50,
      b: Math.floor(Math.random() * 206) + 50
    };
    
    // Lifespan tracking
    this.lifespan = Math.floor(Math.random() * (CONFIG.MAX_LIFESPAN - CONFIG.MIN_LIFESPAN + 1)) + CONFIG.MIN_LIFESPAN;
    this.birthTime = performance.now() / 1000; // Current time in seconds
    this.remainingLife = parseFloat(this.lifespan);
    this.alive = true;
    
    // Test mode variables
    this.testInitialX = this.x;
    this.testInitialY = this.y;
    this.testVx = null;
    this.testVy = null;
  }
  
  update(dt) {
    // Time-based physics update: mirror Python logic exactly
    // Step 1: Random velocity perturbation
    if (Math.random() < CONFIG.VELOCITY_CHANGE_CHANCE) {
      const perturbation = 50 * (this.size / CONFIG.SQUARE_SIZE_MAX);
      const choices = [-1, 0, 1];
      this.vx += choices[Math.floor(Math.random() * 3)] * perturbation;
      this.vy += choices[Math.floor(Math.random() * 3)] * perturbation;
      
      // Clamp speed
      this.vx = Math.max(-CONFIG.MAX_SPEED, Math.min(CONFIG.MAX_SPEED, this.vx));
      this.vy = Math.max(-CONFIG.MAX_SPEED, Math.min(CONFIG.MAX_SPEED, this.vy));
      
      // Avoid fully stopping
      if (this.vx === 0) this.vx = Math.random() < 0.5 ? -50 : 50;
      if (this.vy === 0) this.vy = Math.random() < 0.5 ? -50 : 50;
    }
    
    // Step 2: Move position (velocity × dt)
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    
    // Step 3: Handle screen wrapping
    if (this.x < 0) {
      this.x = CONFIG.WIDTH - this.size;
      this.x = Math.max(0, Math.min(this.x, CONFIG.WIDTH - this.size));
    } else if (this.x + this.size > CONFIG.WIDTH) {
      this.x = 0;
      this.x = Math.max(0, Math.min(this.x, CONFIG.WIDTH - this.size));
    }
    
    if (this.y < 0) {
      this.y = CONFIG.HEIGHT - this.size;
      this.y = Math.max(0, Math.min(this.y, CONFIG.HEIGHT - this.size));
    } else if (this.y + this.size > CONFIG.HEIGHT) {
      this.y = 0;
      this.y = Math.max(0, Math.min(this.y, CONFIG.HEIGHT - this.size));
    }
    
    // Step 4: Update lifespan
    const currentTime = performance.now() / 1000;
    this.remainingLife = this.lifespan - (currentTime - this.birthTime);
    if (this.remainingLife < CONFIG.ROUNDOFF) {
      this.alive = false;
    }
  }
  
  draw(ctx) {
    // Render with visual jitter (±1 pixel scaled by size)
    const jitterX = Math.random() < 0.5 ? -1 : 1;
    const jitterY = Math.random() < 0.5 ? -1 : 1;
    const x = this.x + (jitterX * (this.size / CONFIG.SQUARE_SIZE_MAX) * 1);
    const y = this.y + (jitterY * (this.size / CONFIG.SQUARE_SIZE_MAX) * 1);
    
    // Set fill color using RGB
    ctx.fillStyle = `rgb(${this.color.r}, ${this.color.g}, ${this.color.b})`;
    // Equivalent to pygame.draw.rect(surface, self.color, (x, y, self.size, self.size))
    ctx.fillRect(x, y, this.size, this.size);
    
    // Draw trail line from square to offset position
    ctx.strokeStyle = `rgb(${this.color.r}, ${this.color.g}, ${this.color.b})`;
    ctx.beginPath();
    // Equivalent to pygame.draw.line() from (self.x, self.y) to (self.x - TRAILS_LENGTH, self.y - TRAILS_LENGTH)
    ctx.moveTo(this.x, this.y);
    ctx.lineTo(this.x - CONFIG.TRAILS_LENGTH, this.y - CONFIG.TRAILS_LENGTH);
    ctx.stroke();
  }
  
  checkCollision(other) {
    // Axis-aligned bounding box collision detection
    // Python: rect1.colliderect(rect2)
    // JavaScript: check if two rectangles overlap
    const rect1 = {
      left: this.x,
      top: this.y,
      right: this.x + this.size,
      bottom: this.y + this.size
    };
    const rect2 = {
      left: other.x,
      top: other.y,
      right: other.x + other.size,
      bottom: other.y + other.size
    };
    
    return !(rect1.right < rect2.left || 
             rect1.left > rect2.right || 
             rect1.bottom < rect2.top || 
             rect1.top > rect2.bottom);
  }
}
```

### Spatial Grid Data Structure
Python: `dict[tuple[int, int], list[Square]]`  
JavaScript: `Map<string, Array<Square>>` or plain object with string keys.

Recommendation: Use plain object with stringified coordinates as keys for simplicity:
```javascript
const grid = {};
// Key format: "cellX,cellY"
grid["5,3"] = [square1, square2, ...];
```

---

## Key Functions

### 1. findThreatOrPrey(square, grid)

**Python Signature:**
```python
def find_threat_or_prey(square: Square, grid: dict[tuple[int, int], list[Square]]) 
  -> tuple[Square | None, Square | None]:
```

**JavaScript Translation:**
```javascript
function findThreatOrPrey(square, grid) {
  // Find closest threat (larger) and prey (smaller) in 3×3 grid neighborhood
  let closestThreat = null;
  let closestThreatDist = Infinity;
  let closestPreyDist = Infinity;
  let closestPreyDist = Infinity;
  let closestPrey = null;
  
  const cellX = Math.floor(square.x / CONFIG.CELL_SIZE);
  const cellY = Math.floor(square.y / CONFIG.CELL_SIZE);
  
  // Check 3×3 neighborhood
  for (let dx = -1; dx <= 1; dx++) {
    for (let dy = -1; dy <= 1; dy++) {
      const neighborCell = `${cellX + dx},${cellY + dy}`;
      const neighbors = grid[neighborCell] || [];
      
      for (const neighbor of neighbors) {
        if (neighbor === square) continue;
        
        // Calculate Euclidean distance between centers
        const dxDist = square.x - neighbor.x;
        const dyDist = square.y - neighbor.y;
        const dist = Math.sqrt(dxDist * dxDist + dyDist * dyDist);
        
        // Track threat: larger neighbor within FLEE_RADIUS
        if (neighbor.size > square.size && dist < CONFIG.FLEE_RADIUS) {
          if (dist < closestThreatDist) {
            closestThreat = neighbor;
            closestThreatDist = dist;
          }
        }
        // Track prey: smaller neighbor within CHASE_RADIUS
        else if (neighbor.size < square.size && dist < CONFIG.CHASE_RADIUS) {
          if (dist < closestPreyDist) {
            closestPrey = neighbor;
            closestPreyDist = dist;
          }
        }
      }
    }
  }
  
  return [closestThreat, closestPrey];
}
```

### 2. findCollisionsInGrid(square, grid, dt)

**Python Signature:**
```python
def find_collisions_in_grid(square, grid, dt):
```

**JavaScript Translation:**
```javascript
function findCollisionsInGrid(square, grid, dt) {
  const cellX = Math.floor(square.x / CONFIG.CELL_SIZE);
  const cellY = Math.floor(square.y / CONFIG.CELL_SIZE);
  const neighborCell = `${cellX},${cellY}`;
  const neighbors = grid[neighborCell] || [];
  
  for (const neighbor of neighbors) {
    if (neighbor === square) continue;
    
    // Check collision and apply growth if square is larger
    if (square.checkCollision(neighbor) && square.size > neighbor.size) {
      square.size += (neighbor.size * dt) / CONFIG.GROWTH_SPEED;
      neighbor.alive = false;
    }
  }
}
```

---

## Main Simulation Loop

### Python Structure (pseudo-code):
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    # Initialize squares
    squares = [Square(...) for _ in range(total_count)]
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update all squares
        for square in squares:
            square.update(dt)
        
        # Build spatial grid
        grid = {}
        for square in squares:
            # Add square to all cells it occupies
            ...
        
        # Apply flee/chase behaviors
        for square in squares:
            threat, prey = find_threat_or_prey(square, grid)
            # Update velocity based on threat/prey
            ...
        
        find_collisions_in_grid(square, grid, dt)
        
        # Handle dead squares (replace with new ones)
        survivors = [s for s in squares if s.alive]
        # Add new squares to maintain count
        squares = survivors
        
        # Render
        screen.fill(BG_COLOR)
        for square in squares:
            square.draw(screen)
        pygame.display.flip()
```

### JavaScript Translation:

The main loop will be structured as a **requestAnimationFrame recursive function** that mimics the pygame while-loop.

**Key Components:**

1. **Canvas Setup (equivalent to pygame.init() + pygame.display.set_mode())**
   ```javascript
   const canvas = document.getElementById('canvas');
   const ctx = canvas.getContext('2d');
   canvas.width = CONFIG.WIDTH;
   canvas.height = CONFIG.HEIGHT;
   ```

2. **Time Management**
   ```javascript
   let lastFrameTime = performance.now() / 1000;
   
   function calculateDt() {
     const currentTime = performance.now() / 1000;
     const dt = currentTime - lastFrameTime;
     lastFrameTime = currentTime;
     // Cap dt to avoid large jumps if tab loses focus
     return Math.min(dt, 1 / CONFIG.FPS * 2);
   }
   ```

3. **Animation Loop (equivalent to pygame's while loop + clock.tick())**
   ```javascript
   let running = true;
   
   function gameLoop() {
     if (!running) return;
     
     const dt = calculateDt();
     
     // Process events (keyboard/mouse)
     // (handled via addEventListener outside loop)
     
     // Update all squares
     for (const square of squares) {
       square.update(dt);
     }
     
     // Build spatial grid
     grid = buildGrid(squares);
     
     // Apply flee/chase behaviors
     for (const square of squares) {
       const [threat, prey] = findThreatOrPrey(square, grid);
       const speed = Math.sqrt(square.vx ** 2 + square.vy ** 2) || 1;
       
       if (threat) {
         // Flee: move away from threat
         const dx = square.x - threat.x;
         const dy = square.y - threat.y;
         const dist = Math.sqrt(dx ** 2 + dy ** 2) || 1;
         square.vx = (dx / dist) * speed;
         square.vy = (dy / dist) * speed;
       } else if (prey) {
         // Chase: move toward prey
         const dx = prey.x - square.x;
         const dy = prey.y - square.y;
         const dist = Math.sqrt(dx ** 2 + dy ** 2) || 1;
         square.vx = (dx / dist) * speed;
         square.vy = (dy / dist) * speed;
       }
     }
     
     // Check collisions
     for (const square of squares) {
       findCollisionsInGrid(square, grid, dt);
     }
     
     // Handle dead squares and replacements
     updateSquaresList(squares);
     
     // Render frame
     renderFrame(ctx, squares);
     
     // Continue loop (equivalent to pygame.display.flip() + clock.tick())
     requestAnimationFrame(gameLoop);
   }
   
   // Start the loop
   gameLoop();
   ```

### buildGrid(squares) Helper Function

```javascript
function buildGrid(squares) {
  const grid = {};
  
  for (const square of squares) {
    const cellXMin = Math.floor(square.x / CONFIG.CELL_SIZE);
    const cellXMax = Math.floor((square.x + square.size) / CONFIG.CELL_SIZE);
    const cellYMin = Math.floor(square.y / CONFIG.CELL_SIZE);
    const cellYMax = Math.floor((square.y + square.size) / CONFIG.CELL_SIZE);
    
    for (let cx = cellXMin; cx <= cellXMax; cx++) {
      for (let cy = cellYMin; cy <= cellYMax; cy++) {
        const cellKey = `${cx},${cy}`;
        if (!grid[cellKey]) {
          grid[cellKey] = [];
        }
        grid[cellKey].push(square);
      }
    }
  }
  
  return grid;
}
```

### updateSquaresList(squares) Helper Function

```javascript
function updateSquaresList(squares) {
  // Count dead squares by size
  let deadBig = 0, deadMedium = 0, deadSmall = 0;
  
  for (const square of squares) {
    if (!square.alive) {
      if (square.size === CONFIG.BIG_SQUARE_SIZE) deadBig++;
      else if (square.size === CONFIG.MEDIUM_SQUARE_SIZE) deadMedium++;
      else if (square.size === CONFIG.SMALL_SQUARE_SIZE) deadSmall++;
    }
  }
  
  // Filter out dead squares
  const survivors = squares.filter(s => s.alive);
  
  // Add replacements to maintain count
  for (let i = 0; i < deadBig; i++) {
    survivors.push(new Square(CONFIG.BIG_SQUARE_SIZE));
  }
  for (let i = 0; i < deadMedium; i++) {
    survivors.push(new Square(CONFIG.MEDIUM_SQUARE_SIZE));
  }
  for (let i = 0; i < deadSmall; i++) {
    survivors.push(new Square(CONFIG.SMALL_SQUARE_SIZE));
  }
  
  // Update the squares array in-place or return it
  squares.length = 0;
  squares.push(...survivors);
}
```

### renderFrame(ctx, squares) Helper Function

```javascript
function renderFrame(ctx, squares) {
  // Clear canvas: equivalent to screen.fill(BG_COLOR)
  ctx.fillStyle = `rgb(${CONFIG.BG_COLOR.r}, ${CONFIG.BG_COLOR.g}, ${CONFIG.BG_COLOR.b})`;
  ctx.fillRect(0, 0, CONFIG.WIDTH, CONFIG.HEIGHT);
  
  // Draw all squares: equivalent to pygame.display.flip()
  for (const square of squares) {
    square.draw(ctx);
  }
}
```

---

## Canvas Graphics Translation

### Drawing Methods

| Pygame | Canvas CanvasRenderingContext2D |
|---|---|
| `pygame.draw.rect(surface, color, (x, y, w, h))` | `ctx.fillRect(x, y, w, h)` (after setting `ctx.fillStyle`) |
| `pygame.draw.line(surface, color, (x1, y1), (x2, y2))` | `ctx.beginPath()` → `ctx.moveTo(x1, y1)` → `ctx.lineTo(x2, y2)` → `ctx.stroke()` |
| `screen.fill(color)` | `ctx.fillRect(0, 0, width, height)` (after setting `ctx.fillStyle`) |
| `pygame.display.flip()` | Not needed; canvas updates automatically |

### Color Handling

**Python:** `color = (r, g, b)` tuple  
**JavaScript (Canvas):** `ctx.fillStyle = "rgb(r, g, b)"` string

Example conversion:
```javascript
// Python: pygame.draw.rect(surface, (255, 0, 0), ...)
// JavaScript:
ctx.fillStyle = "rgb(255, 0, 0)";
ctx.fillRect(...);
```

---

## Event Handling

### Quit Event (not applicable to web)
In pygame, `pygame.QUIT` closes the window. In a web application, closing the tab/browser is handled by the user; no special event needed. The `running` flag can be set via a "Stop Simulation" button.

### Optional: Keyboard & Mouse Input
If future features require keyboard or mouse input:

```javascript
// Example: Listen for spacebar to pause
document.addEventListener('keydown', (event) => {
  if (event.key === ' ') {
    running = !running; // Toggle pause
  }
});

// Example: Listen for mouse click
canvas.addEventListener('click', (event) => {
  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;
  // Handle click at (mouseX, mouseY)
});
```

---

## Time Management (dt Calculation)

### Python (pygame):
```python
clock = pygame.time.Clock()
dt = clock.tick(FPS) / 1000.0  # Returns milliseconds, convert to seconds
```

### JavaScript:
```javascript
// Method 1: Using performance.now() (high-resolution timestamp in milliseconds)
let lastFrameTime = performance.now();

function calculateDt() {
  const currentTime = performance.now();
  const dt = (currentTime - lastFrameTime) / 1000; // Convert ms to seconds
  lastFrameTime = currentTime;
  return dt;
}
```

**FPS Regulation:**
- **Pygame:** `clock.tick(FPS)` regulates frame rate.
- **JavaScript:** `requestAnimationFrame()` typically runs at ~60 FPS (depends on display refresh rate).
  - To target a specific FPS, skip frames or use `setTimeout()` instead.
  - For this port, accepting the browser's natural frame rate is acceptable.

**Delta Time Clamping:**
```javascript
// Prevent large dt jumps (e.g., when tab loses focus for a second)
const dt = Math.min(calculateDt(), 1 / CONFIG.FPS * 2);
```

---

## Implementation Checklist

### Phase 1: Boilerplate Setup
- [ ] Create `web/index.html` with minimal HTML structure
- [ ] Set up `<canvas>` element with id="canvas"
- [ ] Create `<script>` block with CONFIG object and helper functions
- [ ] Verify canvas dimensions match Python (800×600)

### Phase 2: Square Class & Utilities
- [ ] Implement `Square` class with `constructor`, `update()`, `draw()`, `checkCollision()`
- [ ] Implement `buildGrid()` for spatial partitioning
- [ ] Implement `findThreatOrPrey()` function
- [ ] Implement `findCollisionsInGrid()` function
- [ ] Implement `updateSquaresList()` for dead square replacement

### Phase 3: Main Loop
- [ ] Implement `calculateDt()` function using `performance.now()`
- [ ] Implement `renderFrame()` function
- [ ] Create `gameLoop()` using `requestAnimationFrame()`
- [ ] Test frame rate and dt calculation

### Phase 4: Initialization
- [ ] Create initial square arrays (big, medium, small)
- [ ] Test square spawning and initial rendering

### Phase 5: Behavior Logic
- [ ] Test square movement and wrapping
- [ ] Test flee behavior (smaller squares flee larger)
- [ ] Test chase behavior (larger squares chase smaller)
- [ ] Test lifespan expiration and square replacement
- [ ] Test collision detection and size growth

### Phase 6: Polish & Documentation
- [ ] Add JSDoc comments mapping pygame equivalents
- [ ] Test visual output (colors, trails, jitter)
- [ ] Optimize if needed (adjust CONFIG parameters)
- [ ] Add optional UI controls (pause, reset, speed adjustment)

### Phase 7: Testing & Validation
- [ ] Compare visual output with original Python version
- [ ] Verify simulation behavior matches predator-prey dynamics
- [ ] Check performance (no noticeable lag)
- [ ] Validate data structures maintain structural parity

---

## Technical Considerations

### JavaScript Floating-Point Arithmetic
- Python's `**` operator → JavaScript's `**` or `Math.pow()`
- `float('inf')` → `Infinity`
- `max()`, `min()` → `Math.max()`, `Math.min()`

### String Keys for Grid Cells
Python uses tuple keys `(cellX, cellY)`. JavaScript objects don't support tuples natively, so use string keys:
```javascript
// Python: grid[(5, 3)] = [square1, ...]
// JavaScript: grid["5,3"] = [square1, ...]
```

### Array vs. List
Python's `list` maps directly to JavaScript's `Array`. Use `.push()`, `.pop()`, `.filter()`, etc.

### Random Number Generation
- `random.randint(a, b)` → `Math.floor(Math.random() * (b - a + 1)) + a`
- `random.uniform(a, b)` → `Math.random() * (b - a) + a`
- `random.choice([1, -1])` → `array[Math.floor(Math.random() * array.length)]`

### Canvas Coordinate System
- **Canvas origin:** Top-left (0, 0)
- **Pygame origin:** Top-left (0, 0)
- ✓ Coordinate systems match—no translation needed

### Color Format Conversion
```javascript
// Store colors as objects for clarity
const color = { r: 255, g: 128, b: 64 };
// Convert to CSS string for canvas
ctx.fillStyle = `rgb(${color.r}, ${color.g}, ${color.b})`;
```

---

## File Structure Summary

The final deliverable will be **one file**: `web/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Predator-Prey Simulation</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #1a1a1a;
            font-family: Arial, sans-serif;
        }
        canvas {
            border: 2px solid #ccc;
            display: block;
        }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    
    <script>
        // ============================================================
        // CONFIG OBJECT & GLOBAL SETUP
        // ============================================================
        // [CONFIG defined here, equivalent to Python constants]
        
        // ============================================================
        // SQUARE CLASS
        // ============================================================
        // [Square class definition]
        
        // ============================================================
        // UTILITY FUNCTIONS
        // ============================================================
        // [buildGrid, findThreatOrPrey, findCollisionsInGrid, etc.]
        
        // ============================================================
        // MAIN LOOP
        // ============================================================
        // [calculateDt, renderFrame, gameLoop initialization]
        
        // ============================================================
        // INITIALIZATION
        // ============================================================
        // [Canvas setup, square array creation, gameLoop start]
    </script>
</body>
</html>
```

---

## Notes for Students

1. **Maintain Structural Parity:** Every class, function, and variable from Python should have a direct JavaScript counterpart. Resist the urge to refactor or optimize at this stage.

2. **Test Incrementally:** Build Phase by Phase. After each phase, verify the output matches expectations.

3. **Time-Based Physics is Critical:** Ensure `dt` calculation is correct. Small errors compound over time, causing drift in simulation behavior.

4. **Spatial Grid Performance:** The grid partitioning is what makes the simulation efficient. Don't skip this; its logic is identical to Python.

5. **Canvas Rendering Order:** Always clear the canvas first (`fillRect` with background), then draw all squares. This prevents trailing artifacts.

6. **Edge Cases:**
   - Ensure squares can grow beyond `SQUARE_SIZE_MAX` (collisions increase size).
   - Handle screen wrapping consistently (wrap, not bounce).
   - Check that lifespan expiration removes squares from the simulation.

---

**End of Porting Plan**

Implementation can begin once this plan is reviewed and approved. The modular structure above makes it easy to develop and test each section independently.
