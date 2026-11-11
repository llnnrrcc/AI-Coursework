# Fitness function (A2)

Status: draft. It covers the three terms in `fitness.py` so far. The neighbouring-feet penalty and the forward-motion reward are not written yet, so the weights below will change when they are.

## What it does

`fitness(chromosome)` turns the 36 genes into 300 frames of joint angles with `decode()` in `gait.py`, finds where each foot is in each frame with `spider_joints()`, and returns one number. Higher is better. The floor numbers come from `DECISIONS.md` section 2: floor at z = -0.30, and a foot counts as planted inside the contact band, -0.35 to -0.25.

## The three terms

All three run from 0 to 1.

- Support: the fraction of frames in which at least 4 feet are planted. The legs walk in two teams of four, so four feet on the ground is what a working gait looks like, and it is the stability the brief asks for.
- Lift: how far each foot rises above the top of the band at its highest point, as a fraction of 0.10 (capped at 1), averaged over the eight feet. 0.10 above the band is about 0.15 above the floor, close to the 0.14 the best wave reached in the floor test. A spider that stands still scores 0.
- Below floor (a penalty): how far the feet go below -0.35, averaged over every foot and frame, divided by 0.033. The deepest any foot can reach is -0.383, so 0.033 is the deepest a foot can be below the band. A deeper dip costs more, so a foot 0.03 below costs three times a foot 0.01 below.

## Weights

Support 1.0, below floor 1.0, lift 0.5.

With lift at 1.0, random chromosomes averaged 0.90 against 1.00 for standing, because a gait with every foot in the air and nothing planted still earns full lift. With lift at 0.5, 200 random chromosomes averaged 0.45 (95th percentile 0.51). Hand-made stepping gaits scored above standing:

| Gait | Score |
| --- | --- |
| Standing | 1.00 |
| Centres at the standing pose, femur and tibia half a step apart | 1.05 |
| Centres femur -0.375, tibia -1.45, half a step apart | 1.25 |
| Centres femur -0.35, tibia -1.4, half a step apart | 0.96 |
| Centres femur -0.35, tibia -1.4, three-eighths of a step apart | 1.17 |

The scores say the best centres sit between the standing pose and the higher ones. Too low and the feet barely lift, too high and fewer than four feet stay planted.

## Why only every 5th frame is scored

One step is 60 frames, so every 5th frame gives 12 samples per step. One call takes about 0.07 s that way, against 0.38 s for all 300 frames. The GA calls it thousands of times: 5,000 calls is about 6 minutes against about 32.

## What I changed along the way

Version 1 rewarded feet inside the contact band. Standing still scored the maximum (1.000), and the term also punished lifting a foot, because a lifted foot is out of the band. That fought the lift term, so I replaced it with the support term (at least 4 feet planted), which does not mind the other four lifting.

## Known limits

- Standing still scores 1.00, and nothing rewards moving forward yet. Until the forward-motion term is written, the only thing pushing the GA towards a walk is the lift reward.
- Support cannot tell a planted foot from a foot that is only passing through the band on its way up or down.

## Still to write

- Neighbouring-feet penalty. L1 and L2's feet come within 0.56 at the turnaround and their segments within 0.49 (`DECISIONS.md` section 3). Threshold and reason to follow.
- Forward-motion reward: planted feet moving backwards (towards -x), which pushes the body forward.
- Re-weigh all five terms together.

## How this was made

Claude proposed the structure (support, lift and below floor) and wrote the code for the three terms and the hand-made gaits above. I ran version 1 myself: standing 1.000, random mean 0.094 over 20 random chromosomes. The scores for the current weights and the hand-made gaits were run with Claude's help and I still need to re-run them on my laptop.
