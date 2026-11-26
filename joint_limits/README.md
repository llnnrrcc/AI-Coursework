# Joint limits: combined 

Sources: `femur_limits.md` , `tibia_limits.md` , `coxa_limits.md` , `coxa_symmetry.md`.
All angles in radians. Slot numbers are positions in the 24-angle vector.

## Limits per leg

### Coxa (different for each leg)

The right side is the left side with the sign flipped.

| Leg | Slot | Min | Max |
|----|---|---|---|
| L1 | 0 | -0.62 | 0.00 |
| L2 | 3 | -0.62 | -0.01 |
| L3 | 6 | -0.54 | +0.38 |
| L4 | 9 | +0.14 | +0.47 |
| R4 | 12 | -0.47 | -0.14 |
| R3 | 15 | -0.38 | +0.54 |
| R2 | 18 | +0.01 | +0.62 |
| R1 | 21 | 0.00 | +0.62 |

### Femur and tibia (same for every leg)

| Joint | Min | Max | Slots |
|---|---|---|---|
| Femur | -0.5 | -0.2 | 1, 4, 7, 10, 13, 16, 19, 22 |
| Tibia | -1.7 | 0.0 | 2, 5, 8, 11, 14, 17, 20, 23 |

## Floor

- Floor at z = -0.30
- A foot counts as planted between z = -0.35 and -0.25
- Feet can only be planted for femur values from -0.5 to about -0.32. The rest of the femur range is for lifting legs during a step.

## Standing pose (proposed)

Femur -0.4 and tibia -1.5 on every leg (Pair A). Coxa at the middle of each leg's range (B1), instead of 0, so every leg can swing both ways:

| Leg | Coxa | Leg | Coxa |
|---|---|---|---|
| L1 | -0.31 | R1 | +0.31 |
| L2 | -0.32 | R2 | +0.32 |
| L3 | -0.08 | R3 | +0.08 |
| L4 | +0.31 | R4 | -0.31 |

Checked in the model: all eight feet sit at z = -0.295, and the nearest neighbouring feet (L1 and L2) are 1.65 apart.

## How the open points were settled

1. Standing pose coxa. We used the middle of each leg's range, as in the table above, because a coxa of 0 left L1 at its backward limit and L4 just outside its range. The middle gives every leg room to swing both ways (`DECISIONS.md` section 2).
2. Neighbouring coxa ranges overlap. L1 and L2 can reach into each other's space, so we put neighbouring legs in opposite teams, half a cycle apart. This means they never swing towards each other at the same time. Their feet still come within 0.56 of each other at the turnaround, so `fitness.py` also penalises feet that get too close (`DECISIONS.md` section 3, `fitness_design.md`).
3. Exact limits or a margin. We kept the exact limits with no margin, because they come from the real spider's measured range. `chromosome.py` uses these values directly.
4. Tidying `tibia_limits.md`. The floor and femur range in that file now match the agreed values (floor -0.30, femur -0.5 to -0.2).


