# A2: Tibia limits

Date: 19 Oct 2026
Tester: Sujan
Setup: L1 only, tibia changed (`angles[2]`). The first pass (main sweep and edge rows below) held the femur at -0.8. The group's agreed femur range is -0.5 to -0.2, so the later sections repeat the sweep across that range. The -0.8 rows are kept as the first-pass evidence.
Angles are in radians (1 rad is about 57 degrees).

## Main sweep

| Tibia angle | Where does the tibia point? | Folds back onto femur? | Looks realistic? | L1 foot z |
| --- | --- | --- | --- | --- |
| -2.0 | curls back in toward the body | yes, sharply | no by my threshold (a plausible tight bend of about 115 degrees, but reach 1.06 is under 1.5 and the foot is rising again) | -0.352 |
| -1.5 | down and out |partly, bent well in but not a hairpin | yes: reach 1.51 meets the 1.5 threshold, foot near its lowest |-0.57|
| -1.0 |down and out, moderate bend |no |yes: reach 2.0 is well above 1.5, foot close to its lowest |-0.548 |
| -0.5 |slightly down, a gentle bend |no |yes, but the foot is a little high for standing: reach 2.43, foot only just below the body |-0.292 |
| 0 | straight out, continuing the femur |no |yes, but no further than this |0.136|
| 0.5 | kinks up past the line of the femur | no | no: the knee bends backward past straight (hyperextension), reach barely improves (2.69) and the foot lifts above the body plane | 0.631 |

## Narrowing the edges

Extra values between -2.0 and -1.5, where the verdict flips. These three rows are calculated from `kinematics.py` and still need to be confirmed by running them in `explore.py` (each should print the z and reach shown here).

| Tibia angle | Where does the tibia point? | Folds back onto femur? | Looks realistic? | L1 foot z |
| --- | --- | --- | --- | --- |
| -1.6 | down and out, a tighter bend | partly | borderline: reach 1.41, just under 1.5 | -0.545 |
| -1.7 | down and in | yes | no: reach 1.32, foot rising | -0.510 |
| -1.8 | down and in | yes | no: reach 1.23, foot rising | -0.466 |

## Sweep across the agreed femur range (-0.5 to -0.2)

Foot z and reach for L1 at the bottom, middle and top of the agreed femur range. These values are calculated from `kinematics.py` (they match an independent run of the same sweep) and still need to be confirmed by running them in `explore.py` with `angles[1]` set to -0.5, -0.35 and -0.2. Reach is measured from the leg's base on the body.

| Tibia | Femur -0.5: z / reach | Femur -0.35: z / reach | Femur -0.2: z / reach | Realistic? |
| --- | --- | --- | --- | --- |
| -2.0 | -0.302 / 1.34 | -0.247 / 1.48 | -0.172 / 1.60 | no at femur -0.5 and -0.35: reach under 1.5, foot rising |
| -1.9 | -0.337 / 1.44 | -0.267 / 1.57 | -0.177 / 1.70 | no at femur -0.5: reach under 1.5 |
| -1.8 | -0.362 / 1.53 | -0.278 / 1.67 | -0.173 / 1.80 | yes, only just at femur -0.5 |
| -1.7 | -0.378 / 1.63 | -0.278 / 1.77 | -0.159 / 1.90 | yes at all three |
| -1.5 | -0.379 / 1.83 | -0.249 / 1.97 | -0.101 / 2.09 | yes at all three, foot below the body |
| -1.4 | -0.365 / 1.93 | -0.220 / 2.07 | -0.058 / 2.18 | yes |
| -1.0 | -0.212 / 2.30 | -0.015 / 2.41 | 0.197 / 2.48 | yes, foot level with the body |
| -0.5 | 0.158 / 2.63 | 0.400 / 2.68 | 0.647 / 2.69 | yes, foot above the body (swing) |
| 0 | 0.640 / 2.74 | 0.894 / 2.71 | 1.141 / 2.65 | yes, straight leg (upper limit) |

| Femur | Lowest foot z | At tibia | Reach stays at 1.5 or more down to tibia |
| --- | --- | --- | --- |
| -0.5 | -0.383 | -1.59 | -1.83 |
| -0.35 | -0.279 | -1.74 | -1.98 |
| -0.2 | -0.177 | -1.89 | -2.10 |

What this shows: at every femur in the range the foot is still getting lower at a tibia of -1.5 (the lowest point is at -1.59 or beyond), so the foot is not yet curling back up at that angle. The binding test is reach, which at femur -0.5 falls under 1.5 just past -1.8. The feet can only get about 0.38 below the body at best (femur -0.5, tibia -1.59), so the ground has to sit close to the body plane and the spider stands low.

## Final check of the tibia limits (-1.7 to 0.0) against the femur range

Every combination of the final tibia range with the femur range was tested on L1 (a fine grid, not just the corners). The femur range was taken as -0.5 to -0.2 and, separately, as -0.5 to 0.0, which is what `femur_limits.md` gives as its result. Values below are foot z / reach, calculated from `kinematics.py`, and should be confirmed by running a few cells in `explore.py`.

| Femur | Tibia -1.7 | Tibia -1.5 | Tibia -1.0 | Tibia -0.5 | Tibia 0.0 |
| --- | --- | --- | --- | --- | --- |
| -0.5 | -0.378 / 1.63 | -0.379 / 1.83 | -0.212 / 2.30 | 0.158 / 2.63 | 0.640 / 2.74 |
| -0.35 | -0.278 / 1.77 | -0.249 / 1.97 | -0.015 / 2.41 | 0.400 / 2.68 | 0.894 / 2.71 |
| -0.2 | -0.159 / 1.90 | -0.101 / 2.09 | 0.197 / 2.48 | 0.647 / 2.69 | 1.141 / 2.65 |
| -0.1 | -0.069 / 1.97 | 0.007 / 2.15 | 0.343 / 2.52 | 0.811 / 2.67 | 1.299 / 2.59 |
| 0.0 | 0.027 / 2.03 | 0.122 / 2.21 | 0.491 / 2.53 | 0.974 / 2.65 | 1.450 / 2.51 |

Results:

- Reach passes everywhere. The lowest reach in the whole grid is 1.63, against the threshold of 1.5, for both femur ranges. The tibia range of -1.7 to 0.0 is accepted.
- Standing depends on the femur. For femur -0.5 to -0.2, the foot is below the body (z under 0) in 42% of the combinations and at least 0.2 below it in 20%. For femur -0.5 to 0.0 those figures are 30% and 12%. Stance poses sit in the corner with the femur near -0.5 and the tibia between -1.7 and -1.0. At femur -0.1 or above the foot is level with or above the body even at tibia -1.7.
- The deepest foot anywhere is z = -0.383 (femur -0.5, tibia about -1.6), so the ground has to sit at about -0.35 for the spider to touch it.
- Swing is possible: raising the tibia from -1.7 toward -0.5 lifts the foot from z = -0.378 to 0.158 at femur -0.5, giving clearance for a leg to leave the ground.
- Open point: the femur range has been quoted three ways (-0.5 to -0.2, -0.5 to 0.0, and a tighter -0.2 to 0.0 from Wang's measurements). The tibia verdict is the same for the first two. A range of -0.2 to 0.0 would leave almost no stance poses, because the foot barely gets below the body, so it needs confirming with A1 before the group fixes it.

## How I'm defining "realistic"

There was no threshold in the brief, so I defined one from measurable tests run on L1 (numbers calculated from `kinematics.py`). First, reach: the foot should stay well outside its own base, so I require a horizontal reach of at least about 1.5 (the body half-width is 1.0). Second, the foot should still be getting lower as the tibia bends, because past the lowest-foot point a deeper bend only curls the leg back up toward the body. In the first pass at femur -0.8 that point was at a tibia of about -1.29, which made the limit -1.5. Across the agreed femur range (-0.5 to -0.2) the lowest-foot point moves to between -1.59 and -1.89, so that test no longer limits anything above about -1.6, and reach becomes the binding test: it stays at or above 1.5 down to about -1.83 at femur -0.5. I therefore set the minimum at -1.7, which keeps reach at 1.63 or more at every femur value and sits at about 97 degrees of flexion, within the figures reported for real spiders (about 90 degrees typical, up to about 111 degrees at the extreme). For the maximum I use 0.0, a straight leg, since a spider's knee does not bend backward past straight; at +0.5 the first pass showed hyperextension and almost no extra reach.

Sources: Gartly, R. L. (2023), _Elucidating the Relationships Between Spider Size, Joint Stiffness, and the Mechanical Frequency Response of the Body_, MSc thesis, Western University, https://ir.lib.uwo.ca/etd/9835 (knee-like joints are held flexed at about 100 degrees interior angle when standing). Wang, Z. et al. (2011), Movement behavior of a spider on a horizontal surface, _Chinese Science Bulletin_ 56(25): 2748-2757, doi:10.1007/s11434-011-4584-y (femur-tibia angle measured between about 69 and 171 degrees, tibia-metatarsus between about 87 and 175 degrees). Both papers report interior angles, where 180 degrees is a straight leg, so flexion from straight (what `angles[2]` uses) is 180 minus the interior angle: about 80 degrees when standing (-1.4 rad) and up to about 111 degrees at the extreme (-1.94 rad). The model has three leg segments and a real leg has seven, so only the model's tibia hinge (femur to tibia) maps reasonably onto these joints.
Note: threshold reasoning drafted with Claude's help; I checked it by running my own sweep.

## My tibia limits

| | Angle (rad) | Reason (one sentence, based on what I saw) |
| --- | --- | --- |
| Minimum | -1.7 | Across the agreed femur range (-0.5 to -0.2) reach is still 1.63 or more at -1.7 and falls under 1.5 at about -1.83 for femur -0.5; about 97 degrees of flexion, inside the 90 to 111 degrees reported for real spiders. (-1.5 would also pass every test and is the safer alternative.) |
| Maximum | 0.0 | Straight leg; a positive tibia (+0.5 tested) hyperextends the knee for almost no extra reach (2.67 to 2.69), and Wang's femur-tibia angle never passes straight. |

## Notes

- Viewed from the side and from above? 
- Anything odd or surprising: foot z is not a straight line in the tibia angle. At femur -0.8 it was lowest at about -1.29 (z = -0.59) and rose again on both sides. In the agreed femur range the lowest point moves to between -1.59 and -1.89, so the same limit gets a different justification.
- Does the limit depend on the femur angle? Yes. The tibia at which reach falls under 1.5 moves from about -1.51 (femur -0.8) to -1.83, -1.98 and -2.10 (femur -0.5, -0.35, -0.2). The limits above are therefore only valid for the agreed femur range, and must be rechecked if A1's range changes.
- Combined check: the final tibia range (-1.7 to 0.0) was checked against the femur range (-0.5 to -0.2, and -0.5 to 0.0). Reach is at least 1.63 everywhere, and the foot only gets below the body when the femur is below about -0.1 and the tibia is below about -1.0. See the final check section above.
- Rejected idea: per-leg limits, so the front legs could be raised like a jumping spider's display posture. Rejected because it needs more bounds to justify, enlarges the GA's search space, and the fitness function rewards stability, so a raised-leg pose would be penalised. A raised-leg pose is a femur lift with the tibia near straight, so it does not change this tibia range.

## Standing pose (done with A1)

Candidate to confirm in `explore.py`: femur -0.5 and tibia -1.4 on all eight legs (calculated foot z -0.365, reach 1.93, near the lowest foot point). The first-pass standing pose from the plan (femur -0.8, tibia -1.2) is outside the agreed femur range.

| Joint | Value (rad) |
| --- | --- |
| Femur | |
| Tibia | |

L1 foot z in the standing pose: 
All eight feet at the same height? 
