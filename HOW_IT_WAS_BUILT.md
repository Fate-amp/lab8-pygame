# How This Program Was Created

This file explains, in simple steps, how the random moving squares program was built.

## 1. Define the goal
The goal was to make a small Pygame app that:
- opens a window
- shows 10 squares
- moves them around continuously
- makes movement feel random
- keeps squares inside the window

Code lines in main.py: 74-101

## 2. Add the libraries
The program uses:
- random: to generate random positions, colors, and direction changes
- sys: to exit cleanly
- pygame: to draw and animate graphics

Code lines in main.py: 1-4

## 3. Create global settings
We added constants near the top of the file for values that control behavior:
- window width and height
- frame rate (FPS)
- number of squares
- square size
- maximum speed
- chance of random direction change

This makes tuning the animation easy without searching through the whole file.

Code lines in main.py: 8-15

## 4. Create a Square class
A class named Square was created to store data and behavior for one square.

Each square has:
- size
- x and y position
- x and y velocity (speed and direction)
- color

### Why use a class?
A class keeps related data and logic together, so handling 10 squares becomes clean and organized.

Code lines in main.py: 18-71

## 5. Initialize each square randomly
In the constructor (__init__):
- each square starts at a random valid position
- each square gets a random starting velocity
- each square gets a random bright color

This makes every run look a little different.

Code lines in main.py: 21-32

## 6. Update movement each frame
In update():
- sometimes velocity changes slightly to create random wandering
- velocity is clamped so speed stays in a safe range
- if velocity becomes zero, it is reset so the square keeps moving
- position is updated using velocity

Code lines in main.py: 34-52

## 7. Add wall bouncing
Still in update():
- if a square touches the left or right wall, x velocity is reversed
- if a square touches the top or bottom wall, y velocity is reversed

This creates a bounce effect and prevents squares from leaving the visible area.

Code lines in main.py: 54-68

## 8. Draw each square
In draw():
- pygame.draw.rect draws the square using its color and position

Code lines in main.py: 70-71

## 9. Build the main game loop
In main():
- initialize Pygame
- create the display window and game clock
- create a list of 10 Square objects
- run a loop that repeats until the user closes the window

Each loop iteration does three main tasks:
1. Handle input/events
2. Update all squares
3. Draw all squares and show the frame

The clock limits the loop to the target FPS for smooth animation.

Code lines in main.py: 74-101

## 10. Clean shutdown
When the window is closed:
- pygame.quit() releases Pygame resources
- sys.exit() ends the program

Code lines in main.py: 103-105

## 11. Run the app
From the project folder:
- activate .venv
- run python main.py

You should see 10 squares moving and bouncing with small random direction changes.

Code lines in main.py: 108-109
