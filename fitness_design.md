# Fitness function (A2)

Status: final. It covers the six terms in `fitness.py`, used for the final GA run.

## What it does

`fitness(chromosome)` turns the 36 genes into 300 frames of joint angles with `decode()` in `gait.py`, finds where each foot is in each frame with `spider_joints()`, and returns one number. Higher is better. The floor numbers come from `DECISIONS.md` section 2: floor at z = -0.30, contact band -0.35 to -0.25. A foot counts as touching the floor when it is at or below -0.25, the top of the band. Below -0.35 it is too deep and is penalised.

## The terms

Three rewards and four penalties. Every term runs from 0 to 1, except forward, which runs from -1 to 1.

- Support (reward): the fraction of frames in which at least 4 feet are touching the floor. The legs walk in two teams of four, so four feet on the ground is what a working gait looks like, and it is the stability the brief asks for.
- Lift (reward): how far each foot rises above the top of the band at its highest point, as a fraction of 0.10 (capped at 1), averaged over the eight feet. It only counts for a foot that touches the floor at some point, so a leg held up in the air earns nothing. 0.10 above the band is about 0.15 above the floor, close to the 0.14 the best wave reached in the floor test. A spider that stands still scores 0.
- Forward (reward): how far feet touching the floor sweep backwards (towards -x, since front is +x) between sampled frames, divided by 0.05 and capped at 1. The body is fixed in this model, so forward motion has to be read from the feet: a planted foot that moves backwards pushes the body forwards. Sliding the wrong way scores below 0, down to -1, so the GA can tell a slightly wrong gait from a very wrong one. 0.05 is the sweep the best hand-made wave reached, so that wave scores about 1.
- Below floor (penalty): how far the feet go below -0.35, averaged over every foot and frame, divided by 0.033. The deepest any foot can reach is -0.383, so 0.033 is the deepest a foot can be below the band. A deeper dip costs more.
- Too high (penalty): how far each foot's highest point is above z = -0.05 (just below body level), as a fraction of 0.5 (capped at 1). The lift reward stops at 1, so before this term a foot at z = 1.4 cost nothing.
- Crowding (penalty): how far neighbouring feet, seen from above, come within 0.5 of each other, as a fraction of 0.5, averaged over the eight neighbouring pairs and every frame. 0.5 is the closest L1 and L2 get in the group's starting gait (0.5 to 0.56, `DECISIONS.md` section 3). The model has no leg thickness, so there is no physical limit to copy. The penalty starts below that distance, so the gait the design plans for is not punished for something the design already accepts.
- Energy (penalty): the total angle each joint travels per step, divided by twice its range (a full swing there and back), averaged over the 24 joints. 0 is standing still, 1 is every joint swinging through its whole range and back in every step. The model has no masses or motors, so less movement for the same walk stands in for less energy. It was added because the brief asks for a fitness that balances speed, stability and energy efficiency.

## Weights

Support 1.0, forward 1.0, below floor 1.0, too high 1.0, crowding 1.0, lift 0.5, energy 0.5. Before energy the best possible score is 2.5 (support 1, forward 1, lift 0.5). Any walk moves its joints, so the energy term always takes something off and a real gait scores below 2.5.

Lift gets half weight because with equal weights a gait with every foot in the air and nothing planted scored as high as standing (random chromosomes averaged 0.90 against 1.00 for standing), so the GA could not tell flying legs from a working gait. Forward gets full weight because without it standing still scored the best possible 1.00 and nothing pushed the GA to walk. The two later penalties get full weight because they rule out poses that look wrong. Energy can take off at most its weight, and a perfect walk scores 2.5 before it, so any energy weight below 1.5 keeps every perfect walk above standing still (1.0). 0.5 leaves a wide margin and still changes which walk the GA picks.

## Check scores

Scored with the current fitness. The hand-made gaits use full-size waves with the femur and tibia half a step apart. `check_fitness()` in `fitness.py` checks this ordering every time `python fitness.py` runs.

| Gait | Score |
| --- | --- |
| Standing | 1.00 |
| Hand-made wave, coxa timing +0.125 (walking forwards) | 1.63 |
| Same, centres femur -0.375 and tibia -1.45 | 1.90 |
| Same two waves, coxa timing -0.125 (walking backwards) | -0.17 and -0.10 |
| 20 random chromosomes | mean -0.65, best 0.83 |

The hand-made waves swing every joint at full size, so they pay a large energy penalty (about 0.7 of the possible 1).

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

Final settings, chosen from the experiments (`experiments.md`): population 80, mutation rate 0.1, tournament size 3, seed 1 (population 80 was the only setting that reached the maximum on every seed, and seed 42 was a poor start). With the energy term the run uses 100 generations, because at 50 the best was still improving.

The best reached 2.354. The final chromosome (`final_best_chromosome.npy`) scores support 1, lift 1, forward 1, 0 on every other penalty, and energy 0.292. The previous final gait (50 generations, before the energy term) scored the maximum 2.5, which is 2.286 under the current fitness (energy 0.429). So the new gait walks just as well with 32% less joint movement.

Most of the progress came early. By generation 22 the best was 2.286, the same score as the previous final gait. The remaining 78 generations only added 0.068 (2.306 at generation 26, 2.315 at 36, 2.354 at 100). That fits the energy term trimming movement once the walk is in place: when support, lift and forward are all 1, moving less is the only way left to improve.

That is also what the energy term does to the gait. The GA settles on the least movement that still maxes the forward and lift caps: every foot lifts 0.10 to 0.11 above the band, right at the 0.10 lift target. It also moves the swinging work onto the middle legs. L1's coxa swings only 0.024 rad and L4's 0.006 rad, so the front and back legs push with the femur and tibia, while L2 and L3 swing their coxas 0.35 and 0.89 rad.

## Why only every 5th frame is scored

One step is 60 frames, so every 5th frame gives 12 samples per step. One call takes about 0.04 to 0.08 s that way, against 0.38 s for all 300 frames. The GA calls it thousands of times: 2,000 calls (40 chromosomes, 50 generations) is about 2 minutes, and the final run (80 chromosomes, 100 generations, about 8,000 calls) about 9 minutes.

## What changed along the way

- Version 1 rewarded feet inside the contact band. Standing still scored the maximum (1.000), and the term also punished lifting a foot, because a lifted foot is out of the band. I replaced it with the support term (at least 4 feet planted), which does not mind the other four lifting.
- The forward term was added because standing still still scored 1.00.
- The too-high term was added because the best evolved gait held a foot at about z = 1.4 and nothing penalised it.
- The crowding term was added because the leg teams do not prevent close approaches: L1 and L2 still come within 0.56 at the turnaround.
- Sinking instead of lifting. What the GA did: a foot only counted as planted inside the band, so a foot below -0.35 counted as not planted. The GA used this for the return stroke: instead of lifting a foot to bring it forward, it dropped it under the floor. In the seeded run, L2, L4 and their right partners never rose above the band (highest points -0.30 and -0.31) and went below it instead (lowest -0.36 and -0.35), and 20% of forward-moving foot steps happened below -0.35. The forward reward was not cancelled, because those feet did not count as planted, and the below-floor penalty for being 0.01 to 0.03 deep was small. Fix (Lauren, commit fbc58bd): a foot at or below -0.25 counts as touching the floor, so a sunk foot moving forwards now cancels forward reward.
- Legs held in the air. What the GA did: after the sinking fix, the seeded run's best held L2 and R2 up the whole time (lowest point -0.09, never near the floor). Lift only looked at a foot's highest point, so those legs earned lift without ever stepping, while the other six legs kept four feet down. How it was found: checking each foot's lowest point. Fix (a): lift only counts for a foot that touches the floor at some point.
- Forward stopped at 0. A gait sliding the wrong way scored the same as one standing still, so the GA could not tell a slightly wrong gait from a very wrong one. This was not seen being exploited, it was a gap in the signal. Fix (b): forward can go down to -1.
- No energy term. The brief asks for a fitness that balances speed, stability and energy efficiency, and the fitness had nothing for energy. The previous final gait also hit the 2.5 maximum by generation 32, after which the GA could not tell it apart from a better one. The energy penalty covers both: the GA now keeps improving after the walk is perfect, by finding a cheaper way to do it.

## Known limits

- Forward and lift both stop at 1. With the energy term the score no longer sticks at a maximum, but the caps still decide the walk: the GA settles on the least movement that still maxes them, so the final gait walks exactly as fast as the forward cap and lifts exactly as high as the lift target. A faster or higher-stepping gait would need higher caps or a speed reward.
- Support cannot tell a planted foot from a foot that is only passing below the top of the band on its way up or down.
- In the earlier population-40 runs the back legs (L4, R4) shuffled rather than lifted: in the seeded 50-generation run their highest point stayed 0.06 below the top of the band. In the final run they lift 0.10, the same as the other legs, so this applies to the weaker runs only.
- The front and back legs' coxas barely move in the final gait (see Final run). It scores perfectly, but it may look stiff, so it is worth checking in `show_best.py`.
- The score does not look at the body or at balance, only at the feet. A gait can score well and still look odd, so `show_best.py` is the real check.

## How this was made

Drafted with Claude's assistance  for structure legibility and flow. I ran `fitness.py` myself on the first version, with these results: standing 1.000, random mean 0.484, best 1.036 over 20 random chromosomes.

The loophole analysis, the re-scored check table, the seeded GA results, the 100-generation run and `check_fitness()` were done with Claude's help. The energy term was proposed and tested in Lauren's session with Claude; I added it to `fitness.py` and ran the final GA, which matched her test run exactly (2.354, energy 0.292).
