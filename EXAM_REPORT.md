## **Boids**

* **Initial impression**:
Initially, I didn't exactly understand a few things (although the comments helped a lot):
1. Why is angle not an instance attribute?
2. What is steer supposed to do? It is a vector, but is it a direction, or a change in direction?
3. How is separation different from cohesion? Just the direction or something else as well?

**random_steer update**
I tried implementing the steer by calculating the angle, add or subtract the spread and recalculate vx and vy by copying what was already in the __init__ function. I clamped the angle so it wouldn't go over 2 pi and under 0 to handle the edge case.

But all the boids crowd on the bottom right corner. I'm not sure if this is normal behavior or a bug? I'm guessing separation will fix this like the instructions suggest?

update: The problem was with how I was clamping the angle. With the previous implementation, when the angle was -50 it would become 0 which was unwanted! I had to bring it back to the circle which was between 0 and 2pi.

**_separation,_alignment,_cohesion update**
It got a bit of reading to realize the logics were the same so I implemented _separation and then copied and modified that for the other 2. The only difference between separation and cohesion was that the steer from separation moved away from nearby boids while cohesion moved towards them.

Bug: The boids were flocking in the bottom right corner. I know the issue is with what I handle velocity update but I don't know how.

update: The issue is with how I'm handling clampSpeed. I was clamping self.speed without doing anything on the velocity. so i figured I should first calculate the current speed based on the steered velocity, then clamp it and then redistribute based on the angle!