# Overview
This project is a single-file pygame simulation of moving squares with predator-prey behavior based on square size.

The code already has good docstrings and type hints, but the Square.update method is long and mixes many responsibilities (movement, boundary handling, grid building, target search, steering, and lifespan updates). This makes debugging and maintenance harder for beginners.

# Refactoring Goals
1. Improve readability by splitting large logic blocks into small helper methods.
2. Improve correctness and safety by handling edge cases such as zero-distance normalization.
3. Reduce duplication in steering math.
4. Keep behavior the same while making complexity and intent clearer.
5. Keep changes beginner-friendly and incremental.

# Step-by-Step Refactoring Plan
## Step 1: Apply small style and naming cleanups (no behavior changes)
What to do:
1. Replace tabs with 4 spaces in method bodies for consistent indentation.
2. Normalize spacing around operators and assignments.
3. Rename short temporary names where meaning is unclear (for example, use target_dx, target_dy only where needed).
4. Remove unnecessary else: pass blocks.

Why this helps:
1. Consistent formatting reduces reading friction.
2. Clear naming helps first-year students trace logic faster.

Inline comment requirement for final code:
1. Add concise comments where naming/format was cleaned to improve readability.
2. Example comment style: "Refactor: normalized spacing and naming for easier tracing (no logic change)."

## Step 2: Extract movement and boundary logic into helper methods
What to do:
1. Move random velocity perturbation into _apply_random_velocity_change().
2. Move position update into _advance_position().
3. Move wall bounce checks into _bounce_off_walls().
4. Keep call order the same as current update method.

Why this helps:
1. Each helper has one job.
2. update() becomes a readable sequence of steps instead of a large block.

Inline comment requirement for final code:
1. Add short comments above each helper call in update() explaining the phase.
2. Add a comment in each helper explaining that behavior is preserved from original code.

Optional before/after snippet:
Before: movement + bounce logic mixed in update().
After: update() calls _apply_random_velocity_change(), _advance_position(), _bounce_off_walls().

## Step 3: Extract grid building and neighbor search
What to do:
1. Move grid construction into _build_spatial_grid(squares).
2. Move target detection into _find_nearest_threat_and_prey(grid).
3. Return (threat, prey) from neighbor search helper.
4. Keep current 3x3 neighborhood query behavior unchanged.

Why this helps:
1. Separates data preparation (grid) from decision logic (target selection).
2. Makes it easier to test and debug target-finding independently.

Inline comment requirement for final code:
1. Add concise comments that mark where grid is built and where nearest targets are selected.
2. Add one comment noting this keeps local-cell optimization logic intact.

## Step 4: Create one shared steering utility to reduce duplication
What to do:
1. Extract speed calculation and vector normalization into a helper such as _direction_to(target) or _normalize(dx, dy).
2. Use this helper in both flee and chase branches.
3. Keep existing flee and chase formulas, including CHASE_STRENGTH blending.

Why this helps:
1. Flee/chase currently repeat similar math.
2. Shared math reduces copy-paste mistakes.

Inline comment requirement for final code:
1. Add comments that explain what was shared and why this improves maintainability.
2. Add one concept comment: "Normalization converts a vector to unit length to keep direction independent from distance."

Optional before/after snippet:
Before: duplicate distance/speed math in both branches.
After: shared helper returns normalized direction and distance.

## Step 5: Add zero-distance guard for safe normalization
What to do:
1. Before dividing by distance, check whether distance == 0 (or near zero).
2. If distance is zero, skip steering for that frame or keep current velocity.
3. Apply the same safety rule to both flee and chase calculations.

Why this helps:
1. Prevents division-by-zero crashes.
2. Makes behavior robust when two entities overlap exactly.

Inline comment requirement for final code:
1. Add a short safety comment at the guard line explaining crash prevention.
2. Keep comment concise and beginner-friendly.

## Step 6: Separate lifespan update into helper
What to do:
1. Move lifespan math into _update_lifespan().
2. Keep threshold logic (ROUNDOFF) unchanged.
3. Call helper at the end of update().

Why this helps:
1. Keeps simulation behavior phases easy to follow.
2. Makes lifecycle logic easier to evolve later.

Inline comment requirement for final code:
1. Add one comment explaining that lifespan is updated after movement/steering each frame.

## Step 7: Clarify per-frame complexity in comments/docstring
What to do:
1. Keep current complexity explanation, but explicitly clarify that total frame cost is affected by updating all squares.
2. Ensure wording matches actual implementation decisions.

Why this helps:
1. Students learn to connect per-entity complexity to total frame complexity.
2. Prevents confusion between per-square and per-frame cost.

Inline comment requirement for final code:
1. Add a concise note that complexity comments describe per-square work and how frame-level cost scales with square count.

# Final Output Requirements (Mandatory)
When this plan is executed, the output MUST:
1. Contain only the refactored code.
2. Include inline comments that explain what changed.
3. Include inline comments that explain why each change improves readability, maintainability, or correctness.
4. Include inline comments that briefly highlight relevant programming concepts.
5. Keep all explanations concise and beginner-friendly.
6. Preserve current behavior and structure as much as possible.

# Key Concepts for Students
1. Single Responsibility Principle: each helper should do one clear task.
2. Refactoring vs rewriting: improve structure without changing behavior.
3. Spatial partitioning: using local cells to avoid full pairwise checks.
4. Vector normalization: separate direction from magnitude.
5. Defensive programming: check edge cases like zero distance before division.
6. Complexity thinking: distinguish per-object cost from per-frame total cost.

# Safety Notes
1. Run the simulation after each step to confirm behavior is unchanged.
2. Refactor one step at a time and commit small changes.
3. If behavior changes unexpectedly, revert only the last step and retest.
4. Keep constants and gameplay tuning values unchanged during structural refactoring.
5. Do not mix feature additions with refactoring; focus only on code clarity and safety.