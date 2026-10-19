## Pair B - B1: Coxa limits (left side)

Setup: one left leg at a time, coxa changed, femur and tibia at 0. Viewed from directly above. Angles in radians (1 rad ≈ 57.3°).

**What counted as "realistic":** the leg doesn't touch or cross its neighbour, stays on its own side of the body, and stays inside the range a real spider uses.

**Real spider ranges** come from Wang et al. (2011), "Movement behavior of a spider on a horizontal surface", Chinese Science Bulletin 56(25), Table 3, doi:10.1007/s11434-011-4584-y. They measure each leg's deflection angle: how far round from the spider's forward axis it points, seen from above.

**Converting coxa to a real angle:** angle from forward ≈ resting angle + (coxa × 57.3). Resting angles in our model: L1 45°, L2 75°, L3 105°, L4 135°.

### Front leg (L1, `angles[0]`)

| Coxa angle (rad) | swing       | contact L2? | Crosses head? |                Looks realistic?                              |
|------------------|-------------|-------------|---------------|     ----------------------------------------                 |
| -0.6             |   forwards  |   no        |      no       |Yes, - 11 degrees, at the forward limit (real minimum 9 degrees)|
| -0.4             |   forwards  |   no        |      no       |         Yes - 22 degrees (most natural)                      |
| -0.2             |   forwards  |   no        |      no       |            Yes   34 degrees                                  |
| 0                |   neither   |   no        |      no       | yes - 45 degrees backward limit.                             |
| 0.2              |   backwards |no (closer)  |    no         |              no - 12 degrees past front leg limit            |
| 0.4              |   backwards |no (parallel L2)|     no     |no 23 degrees past limit - no room for L2 to swing forward    |
| 0.6              |   backwards |  nearly      |      no      |   no 34 degrees past front leg's range                       |

### Back leg (L4, `angles[9]`)

| Coxa angle (rad) | swing      | contact L3? | Crosses the back of the body? | Looks realistic?                              |
|------------------|------------|-------------|-------------------------------|-----------------------------------------------|
| -0.6             | forwards   | nearly (0.5) |          no                  |  no - 42 degrees forward of back leg range    |
| -0.4             | forwards   | no (parallel L3)|          no               |    no - 31 degrees forward of back leg range  |
| -0.2             |  forwards  |   no        |        no                     |    no - 20 degrees forward                    |
| 0                | neither    |   no        |         no                    |      borderline - 8 degrees forward           |
| 0.2              | backwards  |  no         |         no                    |     yes - 146 degrees                         |
| 0.4              | backwards  |   no        |           no                  |      yes   - 158 degrees, near back of range  |
| 0.6              | backwards  |   no        |         no                    |      no - 7 degrees past maximum              |


### Narrowing the edges

Extra values between the main sweep steps, where the verdict flips. Checks whether the paper's limits hold in our model.

| Leg | Coxa angle (rad) | Angle from forward | Contact with neighbour? | Looks realistic? |
|---|---|---|---|---|
| L1 | -0.7 | about 5° | no | no - 4 degrees forward of the real minimum (9°), points almost straight ahead |
| L1 | -0.65 | about 8° | no | no (just) - 1 degree forward of the real minimum |
| L4 | 0.1 | about 141° | no | no (just) - 2 degrees short of where a real back leg's range starts (143°) |
| L4 | 0.15 | about 144° | no | yes - just inside the range |
| L4 | 0.45 | about 161° | no | yes - just inside the back end of the range (162°) |
| L4 | 0.5 | about 164° | no | no (just) - 2 degrees past the real maximum |

None of these touch a neighbour, so every verdict here comes from the paper's range. Each edge falls between two tested values, right where the paper puts it: L1's forward limit between -0.65 and -0.6 (paper: -0.62), L4's lower limit between 0.1 and 0.15 (paper: 0.14), and L4's upper limit between 0.45 and 0.5 (paper: 0.47).

### Result

Each leg needs its own coxa range. One shared range doesn't work, because L1's and L4's realistic ranges don't overlap at all.

| Leg | Coxa min (rad) | Coxa max (rad) | Source |
|---|---|---|---|
| L1 (front) | -0.62 | 0.00 | Tested: realistic from -0.6 to 0, edge confirmed between -0.65 and -0.6. Matches the paper (9° to 45°) |
| L2 | -0.62 | -0.01 | Paper only (39° to 74°), not tested |
| L3 | -0.54 | +0.38 | Paper only (74° to 127°), not tested |
| L4 (back) | +0.14 | +0.47 | Tested: edges confirmed between 0.1 and 0.15, and between 0.45 and 0.5. Matches the paper (143° to 162°) |

- **Front leg:** works forwards of its resting position. Positive values swing it back into L2's space and past where a real front leg stops.
- **Back leg:** works behind its resting position. Negative values swing it forwards into L3, and 0.5 or more goes past a real back leg's maximum.
- **Middle legs:** taken from the paper rather than tested, since they sit between the two end legs we checked. L3 is the only leg whose range covers both sides of its resting position, and it has the largest swing (about 52°).

**Rejected alternative:** one shared coxa range for all legs (e.g. -0.4 to +0.4). It would let front legs swing back into L2 and stop back legs reaching their real working range.

**Why per-leg ranges here, when A2 rejected per-leg tibia limits:** the tibia works the same on every leg, so one range fits all. The coxa doesn't, because each leg is attached at a different angle around the body (45°, 75°, 105°, 135°), so the same coxa value points each leg in a different direction. Per-leg ranges also don't enlarge the search space: each leg still has one coxa gene, just with different bounds.

**Recommendation for the standing pose:** Pair A's standing pose uses coxa 0 on every leg, but 0 is the backward limit for L1 and just outside L4's range. Using the middle of each leg's range instead (about -0.31 for L1 and +0.30 for L4) gives every leg room to swing both ways.

> Notes:
> - The right side mirrors these ranges with the sign flipped (B2 to confirm).
> - The coxa rotates around the vertical axis at the hip, so it never changes foot height. Unlike the femur and tibia, its limits don't depend on the other joints, so no combined sweep was needed.
> - The model's leg lengths and attachment points differ from the real spider, so these ranges should be checked against the model when the gait runs.
> - Angle conversions and Result wording drafted with Claude's help; all poses were run and checked by me in explore.py.