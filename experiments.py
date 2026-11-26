"""
experiments.py - compare GA settings, one setting at a time.

Each setting (population size, mutation rate, tournament size, crossover, selection
method and mutation step size) is changed on its own while the others stay at their
defaults. Every setting is run with several seeds,
so one lucky run does not decide anything.

Run from inside the AI-Coursework folder:
    python experiments.py                       the full set (about an hour)
    python experiments.py --generations 5 --seeds 1 --out test_run      a quick test
    python experiments.py --only CROSSOVER --out experiment_results_crossover
                                                only the crossover comparison
    python experiments.py --only SELECTION MUTATION_STEP --seeds 5 --out experiment_results_selection
                                                the selection and mutation step comparisons

Runs are independent, so they are spread over several CPU cores at once (--workers,
default: all cores but one). Each run is seeded on its own, so the results are the same
whatever the number of workers.

Outputs go in the output folder (default experiment_results):
    runs.jsonl      every run's best and average fitness for every generation
    summary.csv     one row per setting value, averaged over the seeds
    experiment_*.png    one graph per setting comparing the best-fitness curves

If the script stops, run it again. Runs already in runs.jsonl are skipped.
"""

import argparse
import contextlib
import csv
import io
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from unittest import mock

import matplotlib
matplotlib.use("Agg")          # save the graphs to files, do not open windows
import matplotlib.pyplot as plt
import numpy as np

import ga
import operators

# The defaults the experiment was run with (experiments.md). Fixed here, because ga.py's own
# settings later changed to the final ones (population 80), which would change the experiment.
DEFAULTS = {"POPULATION_SIZE": 40,
            "MUTATION_RATE": 0.1,
            "TOURNAMENT_SIZE": 3,
            "CROSSOVER": "leg",
            "SELECTION": "tournament",
            "MUTATION_STEP": 0.05}

VALUES = {"POPULATION_SIZE": [20, 40, 80],
          "MUTATION_RATE": [0.05, 0.1, 0.2],
          "TOURNAMENT_SIZE": [2, 3, 5],
          "CROSSOVER": ["leg", "one_point", "uniform"],
          "SELECTION": ["tournament", "roulette", "rank"],
          "MUTATION_STEP": [0.02, 0.05, 0.1]}

LABELS = {"POPULATION_SIZE": "population size",
          "MUTATION_RATE": "mutation rate",
          "TOURNAMENT_SIZE": "tournament size",
          "CROSSOVER": "crossover",
          "SELECTION": "selection",
          "MUTATION_STEP": "mutation step"}

# Settings this script handles itself; the rest are names in ga.py
OWN_SETTINGS = ("CROSSOVER", "SELECTION", "MUTATION_STEP")


def one_point_crossover(p1, p2, rng):
    """Cut both parents at one random point between genes and swap the tails."""
    cut = rng.integers(1, len(p1))
    return np.concatenate([p1[:cut], p2[cut:]]), np.concatenate([p2[:cut], p1[cut:]])


def uniform_crossover(p1, p2, rng):
    """Take each gene from either parent with equal chance."""
    swap = rng.random(len(p1)) < 0.5
    return np.where(swap, p2, p1), np.where(swap, p1, p2)


# "leg" is the GA's own crossover (whole legs swapped, operators.py). The other two are only
# here to compare it against; they can split a leg's genes between parents.
CROSSOVERS = {"leg": operators.crossover, "one_point": one_point_crossover, "uniform": uniform_crossover}


def roulette_select(population, scores, rng):
    """Pick one chromosome with chance proportional to its score.
    Scores can be negative, so they are shifted to start at 0 first; equal scores pick evenly."""
    weights = scores - scores.min()
    if weights.sum() <= 0:
        return population[rng.integers(len(population))]
    return population[rng.choice(len(population), p=weights / weights.sum())]


def rank_select(population, scores, rng):
    """Pick one chromosome with chance proportional to its rank (worst 1, best N), not its score."""
    ranks = np.empty(len(scores))
    ranks[np.argsort(scores)] = np.arange(1, len(scores) + 1)
    return population[rng.choice(len(population), p=ranks / ranks.sum())]


# "tournament" is the GA's own selection (ga.py). The other two are only here to compare it against.
SELECTIONS = {"tournament": ga.tournament_select, "roulette": roulette_select, "rank": rank_select}


def run_key(settings, seed):
    return (f"{settings['POPULATION_SIZE']}|{settings['MUTATION_RATE']}|{settings['TOURNAMENT_SIZE']}|"
            f"{settings['CROSSOVER']}|{settings['SELECTION']}|{settings['MUTATION_STEP']}|{seed}")


def run_once(settings, seed, generations):
    """Run the GA once with these settings. Returns (best per generation, average per generation)."""
    for name, value in settings.items():
        if name not in OWN_SETTINGS:
            setattr(ga, name, value)      # ga.py reads these names each time it runs
    crossover = CROSSOVERS[settings["CROSSOVER"]]
    select = SELECTIONS[settings["SELECTION"]]
    step = settings["MUTATION_STEP"]
    ga.GENERATIONS = generations
    # ga.py passes its own seeded generator to crossover() and mutate(). Here they get a
    # separate generator seeded from the same seed instead, so each run still depends only
    # on its seed. This is how the results in experiments.md were produced, so keep it to
    # reproduce them exactly. (It was first added when ga.py did not pass its generator.)
    operator_rng = np.random.default_rng(seed + 1000)
    # run_ga prints every generation and saves best_chromosome.npy. Silence the printing and
    # block the save, so an experiment never overwrites the saved best.
    with contextlib.redirect_stdout(io.StringIO()), \
            mock.patch("ga.np.save"), \
            mock.patch.object(ga, "crossover", lambda a, b, *_: crossover(a, b, operator_rng)), \
            mock.patch.object(ga, "tournament_select", select), \
            mock.patch.object(ga, "mutate", lambda c, rate, *_: operators.mutate(c, rate, operator_rng, step)):
        _, best_history, average_history = ga.run_ga(seed)
    return [float(x) for x in best_history], [float(x) for x in average_history]


def last_improvement(best):
    """The generation (counting from 1) after which the best never rose again."""
    last = 1
    for i in range(1, len(best)):
        if best[i] > best[i - 1] + 1e-9:
            last = i + 1
    return last


def load_runs(path, generations):
    runs = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                record = json.loads(line)
                record["settings"].setdefault("CROSSOVER", "leg")   # runs from before the crossover option
                record["settings"].setdefault("SELECTION", "tournament")   # and before these two
                record["settings"].setdefault("MUTATION_STEP", 0.05)
                if record["generations"] == generations:
                    runs[run_key(record["settings"], record["seed"])] = record
    return runs


def summarise(runs, generations, out_dir, groups):
    """Print and save one row per setting value, averaged over the seeds."""
    rows = []
    for name in groups:
        values = VALUES[name]
        for value in values:
            settings = dict(DEFAULTS)
            settings[name] = value
            records = [r for r in runs.values()
                       if r["settings"] == settings and r["generations"] == generations]
            if not records:
                continue
            final_best = [r["best"][-1] for r in records]
            final_avg = [r["average"][-1] for r in records]
            rows.append({
                "setting": LABELS[name], "value": value, "seeds": len(records),
                "final_best_mean": np.mean(final_best), "final_best_std": np.std(final_best),
                "final_average_mean": np.mean(final_avg),
                "gap_mean": np.mean(np.array(final_best) - np.array(final_avg)),
                "last_improvement_mean": np.mean([last_improvement(r["best"]) for r in records]),
            })
    with open(os.path.join(out_dir, "summary.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()})
    print(f"{'setting':16s} {'value':>6s} {'seeds':>5s} {'best':>12s} {'average':>8s} {'gap':>6s} {'stopped improving':>18s}")
    for r in rows:
        print(f"{r['setting']:16s} {r['value']:>6} {r['seeds']:>5} "
              f"{r['final_best_mean']:6.3f}+-{r['final_best_std']:.3f} {r['final_average_mean']:8.3f} "
              f"{r['gap_mean']:6.3f} {r['last_improvement_mean']:18.1f}")


def plot_settings(runs, generations, out_dir, groups):
    """One graph per setting: mean best-fitness curve for each value, with the single runs faint."""
    for name in groups:
        values = VALUES[name]
        plt.figure(figsize=(8, 5))
        for value, colour in zip(values, ["tab:blue", "tab:orange", "tab:green"]):
            settings = dict(DEFAULTS)
            settings[name] = value
            curves = [r["best"] for r in runs.values()
                      if r["settings"] == settings and r["generations"] == generations]
            if not curves:
                continue
            curves = np.array(curves)
            x = np.arange(1, generations + 1)
            for curve in curves:
                plt.plot(x, curve, color=colour, alpha=0.2)
            default_mark = " (default)" if value == DEFAULTS[name] else ""
            plt.plot(x, curves.mean(axis=0), color=colour, linewidth=2,
                     label=f"{value}{default_mark}, final {curves[:, -1].mean():.2f}")
        plt.title(f"Best fitness by {LABELS[name]} (mean of {len(curves)} seeds, single runs faint)")
        plt.xlabel("Generation")
        plt.ylabel("Best fitness")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"experiment_{LABELS[name].replace(' ', '_')}.png"), dpi=100)
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Compare GA settings, one at a time.")
    # 50, the value the experiments in experiments.md used; ga.py itself now runs 100
    parser.add_argument("--generations", type=int, default=50)
    parser.add_argument("--seeds", type=int, default=3, help="seeds per setting (1, 2, 3, ...)")
    parser.add_argument("--out", default="experiment_results")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1),
                        help="runs at the same time (default: all CPU cores but one)")
    parser.add_argument("--only", nargs="+", choices=list(VALUES), default=list(VALUES),
                        help="which settings to compare (default: all of them)")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    runs_path = os.path.join(args.out, "runs.jsonl")
    runs = load_runs(runs_path, args.generations)

    # Every run still to do. The default settings appear in every group but run once.
    tasks = {}
    for name in args.only:
        values = VALUES[name]
        for value in values:
            settings = dict(DEFAULTS)
            settings[name] = value
            for seed in range(1, args.seeds + 1):
                key = run_key(settings, seed)
                if key not in runs:
                    tasks[key] = (settings, seed)

    start = time.time()
    print(f"{len(tasks)} runs to do on {args.workers} workers")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_once, settings, seed, args.generations): (settings, seed)
                   for settings, seed in tasks.values()}
        for done, future in enumerate(as_completed(futures), start=1):
            settings, seed = futures[future]
            best, average = future.result()
            record = {"settings": settings, "seed": seed, "generations": args.generations,
                      "best": best, "average": average}
            runs[run_key(settings, seed)] = record
            with open(runs_path, "a") as f:
                f.write(json.dumps(record) + "\n")
            print(f"[{done}/{len(tasks)}] population {settings['POPULATION_SIZE']}, "
                  f"mutation {settings['MUTATION_RATE']}, tournament {settings['TOURNAMENT_SIZE']}, "
                  f"crossover {settings['CROSSOVER']}, selection {settings['SELECTION']}, "
                  f"step {settings['MUTATION_STEP']}, "
                  f"seed {seed}: final best {best[-1]:.3f} (elapsed {(time.time() - start) / 60:.1f} min)")

    summarise(runs, args.generations, args.out, args.only)
    plot_settings(runs, args.generations, args.out, args.only)
    print(f"Saved results and graphs in {args.out}/")


if __name__ == "__main__":
    main()
