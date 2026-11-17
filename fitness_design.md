# Fitness function (A2)

Status: final. It covers the six terms in `fitness.py`, used for the final GA run.

## What it does

`fitness(chromosome)` turns the 36 genes into 300 frames of joint angles with `decode()` in `gait.py`, finds where each foot is in each frame with `spider_joints()`, and returns one number. Higher is better. The floor numbers come from `DECISIONS.md` section 2: floor at z = -0.30, contact band -0.35 to -0.25. A foot counts as touching the floor when it is at or below -0.25, the top of the band. Below -0.35 it is too deep and is penalised.

## The terms

Three rewards and three penalties. Every term runs from 0 to 1, except forward, which runs from -1 to 1.

- Support (reward): the fraction of frames in which at least 4 feet are touching the floor. The legs walk in two teams of four, so four feet on the ground is what a working gait looks like, and it is the stability the brief asks for.
- Lift (reward): how far each foot rises above the top of the band at its highest point, as a fraction of 0.10 (capped at 1), averaged over the eight feet. It only counts for a foot that touches the floor at some point, so a leg held up in the air earns nothing. 0.10 above the band is about 0.15 above the floor, close to the 0.14 the best wave reached in the floor test. A spider that stands still scores 0.
- Forward (reward): how far feet touching the floor sweep backwards (towards -x, since front is +x) between sampled frames, divided by 0.05 and capped at 1. The body is fixed in this model, so forward motion has to be read from the feet: a planted foot that moves backwards pushes the body forwards. Sliding the wrong way scores below 0, down to -1, so the GA can tell a slightly wrong gait from a very wrong one. 0.05 is the sweep the best hand-made wave reached, so that wave scores about 1.
- Below floor (penalty): how far the feet go below -0.35, averaged over every foot and frame, divided by 0.033. The deepest any foot can reach is -0.383, so 0.033 is the deepest a foot can be below the band. A deeper dip costs more.
- Too high (penalty): how far each foot's highest point is above z = -0.05 (just below body level), as a fraction of 0.5 (capped at 1). The lift reward stops at 1, so before this term a foot at z = 1.4 cost nothing.
- Crowding (penalty): how far neighbouring feet, seen from above, come within 0.5 of each other, as a fraction of 0.5, averaged over the eight neighbouring pairs and every frame. 0.5 is the closest L1 and L2 get in the group's starting gait (0.5 to 0.56, `DECISIONS.md` section 3). The model has no leg thickness, so there is no physical limit to copy. The penalty starts below that distance, so the gait the design plans for is not punished for something the design already accepts.

## Weights

Support 1.0, forward 1.0, below floor 1.0, too high 1.0, crowding 1.0, lift 0.5. The best possible score is 2.5 (support 1, forward 1, lift 0.5).

Lift gets half weight because with equal weights a gait with every foot in the air and nothing planted scored as high as standing (random chromosomes averaged 0.90 against 1.00 for standing), so the GA could not tell flying legs from a working gait. Forward gets full weight because without it standing still scored the best possible 1.00 and nothing pushed the GA to walk. The two later penalties get full weight because they rule out poses that look wrong.

## Check scores

Scored with the current fitness. The hand-made gaits use full-size waves with the femur and tibia half a step apart. `check_fitness()` in `fitness.py` checks this ordering every time `python fitness.py` runs.

| Gait | Score |
| --- | --- |
| Standing | 1.00 |
| Hand-made wave, coxa timing +0.125 (walking forwards) | 1.95 |
| Same, centres femur -0.375 and tibia -1.45 | 2.25 |
| Same two waves, coxa timing -0.125 (walking backwards) | 0.15 and 0.25 |
| 20 random chromosomes | mean -0.52, best 0.97 |

Walking forwards beats standing, walking backwards now scores well below standing because forward goes negative, and random gaits sit below both.

## GA result

`ga.py` now passes its seeded generator to `crossover()` and `mutate()`, so the same seed always gives the same run. With seed 42, population 40 and 50 generations, the best score at generation 50 was:

| Fitness version | Best at generation 50 |
| --- | --- |
| Before the sinking fix | 1.76 |
| After the sinking fix | 1.57 |
| After the lift and forward fixes (current) | 1.96 (average 1.88) |

A lower score after a fix does not mean a worse gait: each fix took away points the GA was getting without walking properly.

With the current fitness and 100 generations, the best reached 2.20 (average 2.11) and was still improving at generation 97. That best chromosome scored support 1.00, lift 0.92, forward 0.74 and no penalties. The experiments (`experiments.md`) also found most runs still improving at generation 50, so more generations helps.

### Final run

Final settings, chosen from the experiments (`experiments.md`): population 80, mutation rate 0.1, tournament size 3, 50 generations, seed 1. Population 80 was the only setting that reached the maximum on every seed. Seed 42 was a poor start (2.13 with population 80), while seeds 1 and 2 both reached 2.5, so the final run uses seed 1.

The best reached the maximum score of 2.5 by about generation 32 and held it, with the average about 2.44 at generation 50. The final chromosome (`final_best_chromosome.npy`) scores support 1, lift 1, forward 1 and 0 on every penalty. Every foot lifts 0.10 to 0.18 above the band, the back legs included, and no foot goes below -0.35.

## Why only every 5th frame is scored

One step is 60 frames, so every 5th frame gives 12 samples per step. One call takes about 0.04 to 0.08 s that way, against 0.38 s for all 300 frames. The GA calls it thousands of times: 2,000 calls (40 chromosomes, 50 generations) is about 2 minutes.

## What changed along the way

- Version 1 rewarded feet inside the contact band. Standing still scored the maximum (1.000), and the term also punished lifting a foot, because a lifted foot is out of the band. I replaced it with the support term (at least 4 feet planted), which does not mind the other four lifting.
- The forward term was added because standing still still scored 1.00.
- The too-high term was added because the best evolved gait held a foot at about z = 1.4 and nothing penalised it.
- The crowding term was added because the leg teams do not prevent close approaches: L1 and L2 still come within 0.56 at the turnaround.
- Sinking instead of lifting. What the GA did: a foot only counted as planted inside the band, so a foot below -0.35 counted as not planted. The GA used this for the return stroke: instead of lifting a foot to bring it forward, it dropped it under the floor. In the seeded run, L2, L4 and their right partners never rose above the band (highest points -0.30 and -0.31) and went below it instead (lowest -0.36 and -0.35), and 20% of forward-moving foot steps happened below -0.35. The forward reward was not cancelled, because those feet did not count as planted, and the below-floor penalty for being 0.01 to 0.03 deep was small. Fix (Lauren, commit fbc58bd): a foot at or below -0.25 counts as touching the floor, so a sunk foot moving forwards now cancels forward reward.
- Legs held in the air. What the GA did: after the sinking fix, the seeded run's best held L2 and R2 up the whole time (lowest point -0.09, never near the floor). Lift only looked at a foot's highest point, so those legs earned lift without ever stepping, while the other six legs kept four feet down. How it was found: checking each foot's lowest point. Fix (a): lift only counts for a foot that touches the floor at some point.
- Forward stopped at 0. A gait sliding the wrong way scored the same as one standing still, so the GA could not tell a slightly wrong gait from a very wrong one. This was not seen being exploited, it was a gap in the signal. Fix (b): forward can go down to -1.

## Known limits

- Forward and lift both stop at 1, so the most the fitness can give is 2.5. The final run reaches it by generation 32, after which the GA cannot tell that gait apart from a better one, which is why the best line goes flat. A higher cap or a speed reward would be needed to keep improving.
- Support cannot tell a planted foot from a foot that is only passing below the top of the band on its way up or down.
- In the earlier population-40 runs the back legs (L4, R4) shuffled rather than lifted: in the seeded 50-generation run their highest point stayed 0.06 below the top of the band. In the final run (population 80) they lift 0.12, so this applies to the weaker runs only.
- The score does not look at the body or at balance, only at the feet. A gait can score well and still look odd, so `show_best.py` is the real check.

## How this was made

Claude proposed the structure (support, lift and below floor) and assisted in writing the code for those three terms and the hand-made gaits. I ran `fitness.py` myself on the first version, with these results: standing 1.000, random mean 0.484, best 1.036 over 20 random chromosomes.

The loophole analysis, the re-scored check table, the seeded GA results, the 100-generation run and `check_fitness()` were done with Claude's help.
