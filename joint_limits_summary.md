# Joint limits: combined (Day 3)

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

## Open points for the group

1. **Agree the standing pose coxa:** Pair A's files use coxa 0, B1 proposes the per-leg middles above.
2. **Neighbouring coxa ranges overlap.** L1 reaches back to 45° and L2 reaches forward to 39°, so the two can cross. With L1 at 0 and L2 at -0.62, their feet are only 0.56 apart. Real spiders avoid this by moving neighbours out of step, so the fitness function needs a penalty for legs getting too close, or the gait needs to keep neighbours in opposite groups.
3. **Exact limits or a margin?** The coxa limits are the real spider's measured range. We could add a small margin (0.05 to 0.1) to give the GA room.
4. **Tidy `tibia_limits.md`:** two older lines still mention a floor of about -0.35 and the femur range as an open point, both now settled.

> Note: combined from the four results files with Claude's help; standing pose and neighbour gaps checked by running the model.