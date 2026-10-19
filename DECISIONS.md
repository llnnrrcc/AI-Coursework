# Design decisions

Draft: joint limits and ground height awaiting group sign-off. Chromosome design to follow in Part 3.

Each decision links to the file holding the full evidence.

## 1. Joint limits

| Joint | Range (rad) | Applies to | Evidence |
|---|---|---|---|
| Coxa | Different for each leg, e.g. L1 -0.62 to 0.00, L4 +0.14 to +0.47 | Per leg, right side mirrored | `coxa_limits.md`, `coxa_symmetry.md` |
| Femur | -0.5 to -0.2 | Every leg | `femur_limits.md` |
| Tibia | -1.7 to 0.0 | Every leg | `tibia_limits.md` |

The full per-leg table with slot numbers is in `joint_limits_summary.md`.

**Why:** femur and tibia limits come from testing L1 for leg shape, reach and whether the foot can reach the ground, checked against each other because they depend on each other. Coxa limits come from testing the front and back legs against real spider measurements (Wang et al., 2011). They differ per leg because each leg is attached at a different angle around the body, so one shared range would let front legs swing into their neighbours and stop back legs reaching their working range.

**Symmetry rule:** right coxa = minus left coxa. Femur and tibia are the same on both sides.

## 2. Ground height and standing pose

- **Floor:** z = -0.30. A foot counts as planted between -0.35 and -0.25.
- **Standing pose:** femur -0.4 and tibia -1.5 on every leg, with coxa at the middle of each leg's range (L1 -0.31, L2 -0.32, L3 -0.08, L4 +0.31, right side mirrored). All eight feet sit at z = -0.295.

**Why:** the deepest any foot can reach is about -0.383, so a floor at -0.30 lets feet plant across about 60% of the femur range, leaving the rest for lifting legs during a step. Coxa at the middle of each range (rather than 0) gives every leg room to swing both ways, since 0 is at the edge of the front and back legs' ranges.

**Rejected:** a floor at -0.35. Feet could only plant across about a third of the femur range, leaving the GA little room, and its below-floor penalty could never trigger. See `femur_limits.md`.

## 3. Chromosome design

## 4. Rejected options