**Before Coding**
I tried to understand the requirements before starting to code and here's what I gathered from what CoPilot said (I'm writing this in steps so that I can get back to it while coding):
1. I add MIN_LIFESPAN and MAX_LIFESPAN to randomize the lifespan at square creation
2. I add an attribute self.lifespan and birth_time to every square. Since time substraction will create floating points, I think I also need a roundoff error so that a number close enough to 0 will be accepted
3. In each update, I subtract the current time from birth_time, if it's 0(or close enough to 0), the square should be removed
4. I should create a new list of survivors(I was thinking of removing the square from the initial list but apparently that's not clean).


**While Coding**
The bugs Copilot helped me figure out without any code:

- Problem1: The squares started going at insane speeds, also the count is MUCH more than the count I set. probably because of how I handled the remaining_life. My initial thought on squares' death logic was wrong

(I figured out what was wrong, they were going at insane speeds because I was calculating remaining_life as current_time-birth_time so at first, remaining_life was 0!)

- Problem2: All squares share the same absolute death because I wasn't using birth_time at all and all squares had the program's birth time as the initial value


**After Coding**
I am trying to go through the improvements mentioned in the code-explorer.html:

1. **The nested threat loop**
Idea: Using grids and grid comparison instead of comparing every square to every other square
2. **Allocating Vector object 5 times** in the inner loop:
Idea to fix: The pygame.Vector2 is easy to use, but it can easily be replaced with maths operations without creating new objects