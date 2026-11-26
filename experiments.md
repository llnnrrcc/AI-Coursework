# GA experiments (A2)

Written by Sujan.

## What was tested

One GA setting was changed at a time, with the other two kept at the defaults `ga.py` had at the time (population 40, mutation rate 0.1, tournament size 3, elitism 2, 50 generations):

- population size: 20, 40, 80
- mutation rate: 0.05, 0.1, 0.2
- tournament size: 2, 3, 5

Each setting was run with seeds 1, 2 and 3, so one lucky run does not decide anything. The default settings appear in all three groups but were run once, so the full set is 21 runs. Every run is seeded, so the same seed always gives the same run.

The fitness is the version after the lift and forward fixes (commit e239a78), before the energy term was added. Scores here are therefore on the old scale, where 2.5 was reachable. The final gait in `fitness_design.md` uses the later fitness, so its 2.354 is not comparable with these numbers. The most it can give is 2.5 (support 1, forward 1, lift 0.5).

To repeat this: `python experiments.py --only POPULATION_SIZE MUTATION_RATE TOURNAMENT_SIZE --out experiment_results_v3`. The fitness has changed since (the energy term and per-leg forward), so a re-run now gives scores on the new scale rather than the numbers below. The summary table and the three graphs from this run are in `results/experiments/`.

## Results

Mean over the three seeds. "Gap" is the best minus the average at generation 50. "Stopped improving" is the last generation where the best went up.

| Setting | Value | Final best | Final average | Gap | Stopped improving |
| --- | --- | --- | --- | --- | --- |
| Population | 20 | 2.220 ± 0.204 | 2.085 | 0.135 | 50.0 |
| Population | 40 (default) | 2.464 ± 0.019 | 2.315 | 0.149 | 49.3 |
| Population | 80 | 2.500 ± 0.000 | 2.401 | 0.099 | 43.0 |
| Mutation rate | 0.05 | 2.282 ± 0.219 | 2.191 | 0.091 | 50.0 |
| Mutation rate | 0.1 (default) | 2.464 ± 0.019 | 2.315 | 0.149 | 49.3 |
| Mutation rate | 0.2 | 2.281 ± 0.310 | 2.117 | 0.164 | 41.3 |
| Tournament size | 2 | 2.214 ± 0.233 | 2.065 | 0.149 | 48.3 |
| Tournament size | 3 (default) | 2.464 ± 0.019 | 2.315 | 0.149 | 49.3 |
| Tournament size | 5 | 2.480 ± 0.029 | 2.340 | 0.140 | 44.7 |

## Findings

Population size. 80 reached the maximum of 2.5 on all three seeds, had the highest average (2.401) and stopped improving earliest (generation 43). 20 was weaker and less consistent (2.220 ± 0.204). This is not a fair fight though: at 50 generations population 80 scores 4,080 chromosomes against 2,040 for population 40, so it gets twice the search for twice the time.

Mutation rate. The default 0.1 was the best and by far the most consistent (2.464 ± 0.019). Both 0.05 and 0.2 averaged about 2.28, and each had one poor run (1.973 at 0.05 and 1.842 at 0.2, both seed 2). 0.2 kept the widest gap (0.164), so more variety in the population, but that did not turn into better results.

Tournament size. 5 was the best of the fair comparisons (2.480 ± 0.029, two of three runs at 2.5). 2 was the weakest setting overall (2.214 ± 0.233). A tournament of 2 gives the least selection pressure, so good chromosomes are picked less often and the GA drifts.

Seed 2. Seed 2 gave the worst run in four settings (population 20, mutation 0.05, mutation 0.2, tournament 2). With population 40 the starting population depends only on the seed, so all the population-40 runs with seed 2 started from the same chromosomes. The default settings and tournament 5 recovered from that start (2.475 and 2.500), the others did not. So the default settings are the most robust to a poor start, not just the best on average.

Early convergence. The task assumed the average catches up with the best by generation 9. The runs do not show that. At generation 9 the gap between best and average was between 0.09 and 0.45 (0.16 to 0.20 for the default settings), and at generation 50 it was still 0.09 to 0.16 on average. Most runs were also still improving near the end (stopped improving at 41 to 50), so 50 generations is too few for the GA to settle, rather than the population converging too early.

The ceiling. 8 of the 21 runs reached exactly 2.5. Once runs hit the maximum, the final best cannot tell settings apart, so the average and the "stopped improving" generation are the better comparisons for the top settings.

## Crossover comparison

The GA's crossover swaps whole legs: each child takes every leg's 9 genes from one parent or the other (`DECISIONS.md` section 3). The reason given was that a leg's coxa, femur and tibia genes only work as a set, so mixing them between parents should break working steps. This was tested against two standard crossovers:

- 1-point: cut both parents at one random place in the 36 genes and swap the ends.
- Uniform: take each gene from either parent at random.

Everything else stayed at the experiment defaults (population 40, mutation rate 0.1, tournament size 3, 50 generations), with seeds 1, 2 and 3. These runs use the current fitness (with the energy term and per-leg forward), so the scores are on a different scale from the table above. Run with `python experiments.py --only CROSSOVER --out experiment_results_crossover`; the graph is `results/experiments/experiment_crossover.png`.

| Crossover | Best at generation 10 | Best at generation 25 | Final best | Final average |
| --- | --- | --- | --- | --- |
| Leg-block (ours) | 1.563 | 1.727 | 1.894 ± 0.141 | 1.750 |
| 1-point | 1.573 | 1.759 | 1.884 ± 0.114 | 1.728 |
| Uniform | 1.433 | 1.798 | 1.936 ± 0.063 | 1.774 |

Mean of the three seeds. Per seed, the final bests were 1.998, 1.694 and 1.989 for leg-block, 1.987, 1.726 and 1.940 for 1-point, and 1.943, 1.856 and 2.010 for uniform.

The test did not support the reason leg-block was chosen. All three ended within 0.052 of each other, which is smaller than the spread between seeds (standard deviation up to 0.141), so none of them is clearly better. Uniform started slowest (1.433 at generation 10, against about 1.57 for the other two) but caught up by generation 25 and finished highest with the smallest spread. Seed 2 was the weakest run for all three.

A likely reason the expected penalty did not show up: every gene keeps its own range whichever parent it comes from, so a mixed leg still decodes to a valid wave inside the joint limits, and the leg team timing is fixed by the design rather than carried by crossover. Breaking up a leg's genes produces a different leg, not a broken one, and mutation and selection can then smooth out any mismatch over later generations.

Leg-block crossover was kept for the final run. It did no worse than the others and matches how the chromosome is organised, but the claim that it protects working steps is not backed by this result. With three seeds and 50 generations, a small advantage either way could still be hidden by the spread.

## Recommended settings

Mutation rate 0.1 and tournament size 5. Population 40, or 80 if the extra time is acceptable (about twice as long per run). The gain from tournament 5 over 3 (2.480 against 2.464) is smaller than the spread between seeds, so it is a weak preference, not a clear win. Running more than 50 generations is likely to help more than any of these settings, since most runs were still improving at the end.

## Limits

- Three seeds is few. Differences smaller than about 0.2 between settings are inside the run-to-run spread.
- Changing one setting at a time does not show how settings interact (for example a bigger population with a higher mutation rate).
- These numbers are for this version of the fitness only. An earlier run on the fitness before the sinking fix gave different numbers (population 20 averaged 1.913 then, against 2.220 now).

## How this was made

`experiments.py` was written by Claude and run by Sujan. This write-up was drafted with Claude's help from `summary.csv` and `runs.jsonl`. See also the AI-use statement in `CONTRIBUTIONS.md`.
