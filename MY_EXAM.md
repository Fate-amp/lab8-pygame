**Exercise 3:**
idea: I have to change the update function where it updates the square's position on bouncing. I'm guessing it's only about setting x and y to the opposite side and NOT multiplying velocity by -1
wait, but the squares disappeared completely after some time

**Exercise 5:**
First impression:I know I have to implement this before respawning and I have to kill a square(set self.alive to 0) when the collision function returns True. It should be close to the logic of the lifespan algorithm
Bug1:self has no attribute "collideRect"
Bug2:The collision does not kill.

**Exercise 6:**
First impression: I should add the size of the smaller square to the bigger one when they collide

**Exercise 7:**
First impression was to somehow control the draw so that the trail can be seen instead of the screen clearing after every frame
I drew the line and the length is 30 but it is not the past trajectory

