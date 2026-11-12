# Fitness function (A2)

Status: draft. It covers the six terms now in `fitness.py`. Weights and thresholds are open to change once the group has run the GA a few more times.

## What it does

`fitness(chromosome)` turns the 36 genes into 300 frames of joint angles with `decode()` in `gait.py`, finds where each foot is in each frame with `spider_joints()`, and returns one number. Higher is better. The floor numbers come from `DECISIONS.md` section 2: floor at z = -0.30, and a foot counts as planted inside the contact band, -0.35 to -0.25. Every term runs from 0 to 1.

## The terms

Three rewards and three penalties.

- Support (reward): the fraction of frames in which at least 4 feet are planted. The legs walk in two teams of four, so four feet on the ground is what a working gait looks like, and it is the stability the brief asks for.
- Lift (reward): how far each foot rises above the top of the band at its highest point, as a fraction of 0.10 (capped at 1), averaged over the eight feet. 0.10 above the band is about 0.15 above the floor, close to the 0.14 the best wave reached in the floor test. A spider that stands still scores 0.
- Forward (reward): how far planted feet sweep backwards (towards -x, since front is +x) between sampled frames, divided by 0.05 and capped at 1. The body is fixed in this model, so forward motion has to be read from the feet: a planted foot that moves backwards pushes the body forwards. A planted foot that slides forwards cancels the reward. 0.05 is the sweep the best hand-made wave reached, so that wave scores about 1.
- Below floor (penalty): how far the feet go below -0.35, averaged over every foot and frame, divided by 0.033. The deepest any foot can reach is -0.383, so 0.033 is the deepest a foot can be below the band. A deeper dip costs more.
- Too high (penalty): how far each foot's highest point is above z = -0.05 (just below body level), as a fraction of 0.5 (capped at 1). The lift reward stops at 1, so before this term a foot at z = 1.4 cost nothing.
- Crowding (penalty): how far neighbouring feet, seen from above, come within 0.5 of each other, as a fraction of 0.5, averaged over the eight neighbouring pairs and every frame. 0.5 is the closest L1 and L2 get in the group's starting gait (0.5 to 0.56, `DECISIONS.md` section 3). The model has no leg thickness, so there is no physical limit to copy. The penalty starts below that distance, so the gait the design plans for is not punished for something the design already accepts.

## Weights

Support 1.0, forward 1.0, below floor 1.0, too high 1.0, crowding 1.0, lift 0.5. The best possible score is 2.5 (support 1, forward 1, lift 0.5).

Lift gets half weight because with equal weights a gait with every foot in the air and nothing planted scored as high as standing (random chromosomes averaged 0.90 against 1.00 for standing), so the GA could not tell flying legs from a working gait. Forward gets full weight because without it standing still scored the best possible 1.00 and nothing pushed the GA to walk. The two later penalties get full weight because they rule out poses that look wrong.

| Gait | Score |
| --- | --- |
| Standing | 1.00 |
| Hand-made wave, coxa timing +0.125 | 1.95 |
| Same, centres femur -0.375 and tibia -1.45 | 2.25 |
| Same two waves, coxa timing -0.125 (walking backwards) | 1.05 and 1.25 |
| 20 random chromosomes | mean -0.15, best 0.92 |

The ordering is the one I wanted: standing is beaten by walking forwards, and random gaits sit well below standing. Walking backwards earns nothing but is not punished, because the forward term stops at 0.

## GA result

I ran `ga.py` (population 40, 50 generations) with this fitness. The best score rose from 0.48 in generation 1 to 1.996 in generation 50, and the average from -0.16 to 1.84. The best was still creeping up at the end, and the most the fitness can give is 2.5.

Another run of the same code, done with Claude's help, reached 2.29. The runs differ because `operators.py` draws its random numbers from `np.random` without a seed, so the `seed` argument in `run_ga()` does not make a run repeatable. In that run the best chromosome scored support 1.00, lift 0.63, forward 0.99, below floor 0.02, too high 0 and crowding 0, and every foot's highest point was at or below z = -0.11, so no foot flies off.

## Why only every 5th frame is scored

One step is 60 frames, so every 5th frame gives 12 samples per step. One call takes about 0.04 to 0.08 s that way, against 0.38 s for all 300 frames. The GA calls it thousands of times: 2,000 calls (40 chromosomes, 50 generations) is about 2 minutes.

## What changed along the way

- Version 1 rewarded feet inside the contact band. Standing still scored the maximum (1.000), and the term also punished lifting a foot, because a lifted foot is out of the band. I replaced it with the support term (at least 4 feet planted), which does not mind the other four lifting.
- The forward term was added because standing still still scored 1.00.
- The too-high term was added because the best evolved gait held a foot at about z = 1.4 and nothing penalised it.
- The crowding term was added because the leg teams do not prevent close approaches: L1 and L2 still come within 0.56 at the turnaround.

## Known limits

- Forward stops at 1, so the GA gets no extra reward for walking faster than 0.05 per sampled frame.
- Support cannot tell a planted foot from a foot that is only passing through the band on its way up or down.
- The score does not look at the body or at balance, only at the feet. A gait can score well and still look odd, so `show_best.py` is the real check.

## How this was made

Claude proposed the structure (support, lift and below floor) and assisted in writing the code for those three terms and the hand-made gaits. I ran `fitness.py` myself on the first version, with these results: standing 1.000, random mean 0.484, best 1.036 over 20 random chromosomes.
