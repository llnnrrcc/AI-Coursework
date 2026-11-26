# GA experiments (A2)

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

## Selection and mutation step comparison

Two more operator choices were tested the same way, on the current fitness, with five seeds instead of three so that closer results could be told apart.

Selection methods:

- Tournament (ours): pick 3 at random, the fittest wins.
- Roulette wheel: chance proportional to fitness. Fitness can be negative here (the below-floor penalty), so scores are shifted to start at 0 first.
- Rank: chance proportional to rank (worst 1, best 40) instead of the score itself.

Mutation step sizes (the spread of each change, as a fraction of the gene's range): 0.02, 0.05 (ours) and 0.1.

Everything else stayed at the experiment defaults (population 40, mutation rate 0.1, tournament size 3, leg-block crossover, 50 generations), with seeds 1 to 5. Run with `python experiments.py --only SELECTION MUTATION_STEP --seeds 5 --out experiment_results_selection`; the graphs are `results/experiments/experiment_selection.png` and `experiment_mutation_step.png`, and the table is `selection_summary.csv`. Tournament with step 0.05 is the same run in both groups, and its seeds 1 to 3 repeat the leg-block runs in the crossover comparison exactly (1.998, 1.694, 1.989).

| Setting | Best at generation 10 | Best at generation 25 | Final best | Final average |
| --- | --- | --- | --- | --- |
| Tournament (ours) | 1.599 | 1.785 | 1.941 ± 0.124 | 1.806 |
| Roulette wheel | 1.407 | 1.648 | 1.855 ± 0.130 | 1.669 |
| Rank | 1.429 | 1.696 | 1.852 ± 0.092 | 1.744 |
| Step 0.02 | 1.434 | 1.581 | 1.671 ± 0.205 | 1.591 |
| Step 0.05 (ours) | 1.599 | 1.785 | 1.941 ± 0.124 | 1.806 |
| Step 0.1 | 1.662 | 1.883 | 2.022 ± 0.198 | 1.808 |

Mean of the five seeds. Per seed (1 to 5), the final bests were 1.998, 1.694, 1.989, 2.009 and 2.014 for tournament with step 0.05; 1.794, 1.881, 1.852, 1.674 and 2.074 for roulette; 1.808, 1.854, 1.731, 2.012 and 1.855 for rank; 1.445, 1.599, 1.936, 1.486 and 1.891 for step 0.02; and 2.045, 1.634, 2.167, 2.128 and 2.134 for step 0.1.

Tournament selection is the best supported of the three. It finished highest on average (1.941, about 0.09 above the other two) and had the highest population average (1.806), and it was well ahead early on: 1.599 at generation 10 against 1.407 for roulette and 1.429 for rank. The final gap is smaller than the spread between seeds, though, and tournament beat each of the others on only three of the five seeds, so the clearest difference is speed rather than the final result. Roulette is likely held back by how close the scores are: late in a run the population average sits only about 0.1 to 0.2 below the best, so a good chromosome is barely more likely to be picked than an average one. Tournament and rank only compare scores, so they don't depend on how far apart the scores are.

The mutation step size mattered more. Step 0.02 was the worst on every one of the five seeds and ended 0.27 below 0.05 on average: changes that small can't move a gait far enough in 50 generations. Step 0.1 finished 0.08 above 0.05 and won on four of the five seeds, losing only on seed 2, which was the weakest seed for every setting. Every run was still improving near generation 50, though, and bigger steps help most when there are few generations left, so 0.1 might not stay ahead over the 100 generations of the final run.

The final run used tournament selection and step 0.05, and both were kept rather than re-running the final GA. Tournament is backed by this test. Step 0.1 is a reasonable change to try in a longer run, but changing it now would mean re-running the final GA and retraining the network on a new gait.

## Recommended settings

Mutation rate 0.1 and tournament size 5. Population 40, or 80 if the extra time is acceptable (about twice as long per run). The gain from tournament 5 over 3 (2.480 against 2.464) is smaller than the spread between seeds, so it is a weak preference, not a clear win. Running more than 50 generations is likely to help more than any of these settings, since most runs were still improving at the end.

## Limits

- Three seeds is few. Differences smaller than about 0.2 between settings are inside the run-to-run spread. The selection and mutation step comparison used five seeds, which narrows this but does not remove it.
- Changing one setting at a time does not show how settings interact (for example a bigger population with a higher mutation rate).
- These numbers are for this version of the fitness only. An earlier run on the fitness before the sinking fix gave different numbers (population 20 averaged 1.913 then, against 2.220 now).
