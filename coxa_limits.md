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

### Result

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

- **Coxa minimum:** ___ rad, because ___
- **Coxa maximum:** ___ rad, because ___
- **Front and back legs need different ranges?** ___