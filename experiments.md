# GA experiments (A2)

## What I tested

I changed one GA setting at a time and kept the other two at their defaults in `ga.py` (population 40, mutation rate 0.1, tournament size 3, elitism 2, 50 generations):

- population size: 20, 40, 80
- mutation rate: 0.05, 0.1, 0.2
- tournament size: 2, 3, 5

Each setting was run with seeds 1, 2 and 3, so one lucky run does not decide anything. The default settings appear in all three groups but were run once, so the full set is 21 runs. Every run is seeded, so the same seed always gives the same run.

The fitness is the version after the lift and forward fixes (commit e239a78). The most it can give is 2.5 (support 1, forward 1, lift 0.5).

To repeat this: `python experiments.py --out experiment_results_v3`. The results and graphs stay out of git (`.gitignore`), so the numbers are copied here.

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

## What I found

Population size. 80 reached the maximum of 2.5 on all three seeds, had the highest average (2.401) and stopped improving earliest (generation 43). 20 was weaker and less consistent (2.220 ± 0.204). This is not a fair fight though: at 50 generations population 80 scores 4,080 chromosomes against 2,040 for population 40, so it gets twice the search for twice the time.

Mutation rate. The default 0.1 was the best and by far the most consistent (2.464 ± 0.019). Both 0.05 and 0.2 averaged about 2.28, and each had one poor run (1.973 at 0.05 and 1.842 at 0.2, both seed 2). 0.2 kept the widest gap (0.164), so more variety in the population, but that did not turn into better results.

Tournament size. 5 was the best of the fair comparisons (2.480 ± 0.029, two of three runs at 2.5). 2 was the weakest setting overall (2.214 ± 0.233). A tournament of 2 gives the least selection pressure, so good chromosomes are picked less often and the GA drifts.

Seed 2. Seed 2 gave the worst run in four settings (population 20, mutation 0.05, mutation 0.2, tournament 2). With population 40 the starting population depends only on the seed, so all the population-40 runs with seed 2 started from the same chromosomes. The default settings and tournament 5 recovered from that start (2.475 and 2.500), the others did not. So the default settings are the most robust to a poor start, not just the best on average.

Early convergence. The task assumed the average catches up with the best by generation 9. The runs do not show that. At generation 9 the gap between best and average was between 0.09 and 0.45 (0.16 to 0.20 for the default settings), and at generation 50 it was still 0.09 to 0.16 on average. Most runs were also still improving near the end (stopped improving at 41 to 50), so 50 generations is too few for the GA to settle, rather than the population converging too early.

The ceiling. 8 of the 21 runs reached exactly 2.5. Once runs hit the maximum, the final best cannot tell settings apart, so the average and the "stopped improving" generation are the better comparisons for the top settings.

## What I would use

Mutation rate 0.1 and tournament size 5. Population 40, or 80 if the extra time is acceptable (about twice as long per run). The gain from tournament 5 over 3 (2.480 against 2.464) is smaller than the spread between seeds, so it is a weak preference, not a clear win. Running more than 50 generations is likely to help more than any of these settings, since most runs were still improving at the end.

## Limits

- Three seeds is few. Differences smaller than about 0.2 between settings are inside the run-to-run spread.
- Changing one setting at a time does not show how settings interact (for example a bigger population with a higher mutation rate).
- These numbers are for this version of the fitness only. An earlier run on the fitness before the sinking fix gave different numbers (population 20 averaged 1.913 then, against 2.220 now).

## How this was made

`experiments.py` was written by Claude, and I ran it. This write-up was drafted with Claude's help from `summary.csv` and `runs.jsonl`.
