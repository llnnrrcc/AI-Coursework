# Design decisions

Draft: joint limits and ground height awaiting group sign-off. Chromosome design drafted in section 3, awaiting sign-off.

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

A chromosome is 72 genes: for each of the 24 joints, three numbers (offset, amplitude, phase). Each joint angle over the 300 frames is a repeating wave:

`angle(t) = offset + amplitude * sin(2 * pi * 5 * t / 300 + phase)`

Smooth by design, so there are no sudden jumps between frames. 5 whole cycles in 300 frames means one step takes 60 frames.

| Joint | Offset | Max amplitude | Limits |
|---|---|---|---|
| Femur | -0.4 | 0.1 | -0.5 to -0.2 |
| Tibia | -1.5 | 0.2 | -1.7 to 0.0 |
| Coxa L1 | -0.31 | 0.31 | -0.62 to 0.00 |
| Coxa L2 | -0.32 | 0.30 | -0.62 to -0.01 |
| Coxa L3 | -0.08 | 0.46 | -0.54 to +0.38 |
| Coxa L4 | +0.31 | 0.16 | +0.14 to +0.47 |

Right-side coxa: same amplitude, offset sign flipped. Femur and tibia are the same on every leg.

**Why:** the offsets are the standing pose from section 2, and each maximum amplitude is the distance from the offset to the nearest limit, so no wave leaves its joint's range. Whole cycles loop cleanly: the gap between the last and first frame equals one normal frame step (checked on all eight legs). Cycle count changes only speed, so 5 is a judgment call (1 cycle looks like slow motion, 8 looks jittery on the plot).

**Known weakness:** a pure wave cannot hold a foot still on the ground for part of the step. Worse, the standing pose sits on the floor, so a wave centred on it puts about 32% of frames below -0.35 (foot z runs from -0.378 to -0.125 over a cycle) and the below-floor penalty fires constantly. Open for the group: centre the offsets above the standing pose (for example femur -0.35, tibia -1.4, not yet tested), or add a duty-cycle gene or a flattened bottom in a second version.

**Origin:** the wave design was proposed by Claude. The cycle and floor numbers were run in the model with Claude's help.

## 4. Rejected options