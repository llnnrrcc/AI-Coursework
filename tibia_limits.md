# A2: Tibia limits

Date: 19 Oct 2026
Tester: Sujan
Setup: L1 only. Femur held at -0.8 (`angles[1] = -0.8`), tibia changed (`angles[2]`).
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

## How I'm defining "realistic"

There was no threshold in the brief, so I defined one from two measurable tests, run on L1 with the femur held at -0.8 (numbers calculated from `kinematics.py`). First, reach: the foot should stay well outside its own base, so I require a horizontal reach of at least about 1.5 (the body half-width is 1.0). Second, diminishing returns: the foot is lowest at a tibia of about -1.29 (z = -0.59), and bending further only curls it back up toward the body (z = -0.35 and reach 1.06 at -2.0). This gives a provisional minimum of about -1.5 rad (roughly 86 degrees of flexion, z = -0.57, reach 1.51), which also fits the reading that useful flexion at a joint tops out around 90 degrees (1.57 rad), occasionally a little more. For the maximum I use 0.0, a straight leg, since a spider's knee does not bend backward past straight. These limits depend on the femur angle (the lowest-foot point moves from -0.89 at femur -1.2 to -1.69 at femur -0.4), so they must be checked against A1's femur range.

Sources: Gartly, R. L. (2023), _Elucidating the Relationships Between Spider Size, Joint Stiffness, and the Mechanical Frequency Response of the Body_, MSc thesis, Western University, https://ir.lib.uwo.ca/etd/9835 (knee-like joints are held flexed at about 100 degrees interior angle when standing). Wang, Z. et al. (2011), Movement behavior of a spider on a horizontal surface, _Chinese Science Bulletin_ 56(25): 2748-2757, doi:10.1007/s11434-011-4584-y (femur-tibia angle measured between about 69 and 171 degrees, tibia-metatarsus between about 87 and 175 degrees). Both papers report interior angles, where 180 degrees is a straight leg, so flexion from straight (what `angles[2]` uses) is 180 minus the interior angle: about 80 degrees when standing (-1.4 rad) and up to about 111 degrees at the extreme (-1.94 rad). The model has three leg segments and a real leg has seven, so only the model's tibia hinge (femur to tibia) maps reasonably onto these joints.
Note: threshold reasoning drafted with Claude's help; I checked it by running my own sweep.

## My tibia limits

| | Angle (rad) | Reason (one sentence, based on what I saw) |
| --- | --- | --- |
| Minimum | -1.5 | Foot is within 0.02 of its lowest height (z = -0.57), reach 1.51; by -1.6 reach has already dropped under 1.5, and past -1.7 the foot rises and tucks under the body. |
| Maximum | 0.0 | Straight leg; a positive tibia (+0.5 tested) hyperextends the knee for almost no extra reach (2.67 to 2.69), and Wang's femur-tibia angle never passes straight. |

## Notes

- Viewed from the side and from above? 
- Anything odd or surprising: foot z is not a straight line in the tibia angle. It is lowest at about -1.29 (z = -0.59) and rises again on both sides, so a more negative tibia does not always lower the foot.
- Does the limit depend on the femur angle? Yes. The lowest-foot tibia moves from -0.89 at femur -1.2 to -1.69 at femur -0.4, so these limits were tested at femur -0.8 only and must be checked against A1's femur range.
- Rejected idea: per-leg limits, so the front legs could be raised like a jumping spider's display posture. Rejected because it needs more bounds to justify, enlarges the GA's search space, and the fitness function rewards stability, so a raised-leg pose would be penalised. A raised-leg pose is a femur lift with the tibia near straight, so it does not change this tibia range.

## Standing pose (done with A1)

| Joint | Value (rad) |
| --- | --- |
| Femur | |
| Tibia | |

L1 foot z in the standing pose: 
All eight feet at the same height? 
