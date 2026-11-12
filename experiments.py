"""
experiments.py - compare GA settings, one setting at a time.

Each of population size, mutation rate and tournament size is changed on its own while
the other two stay at their defaults in ga.py. Every setting is run with several seeds,
so one lucky run does not decide anything.

Run from inside the AI-Coursework folder:
    python experiments.py                       the full set (about an hour)
    python experiments.py --generations 5 --seeds 1 --out test_run      a quick test

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
from unittest import mock

import matplotlib
matplotlib.use("Agg")          # save the graphs to files, do not open windows
import matplotlib.pyplot as plt
import numpy as np

import ga
import operators

DEFAULTS = {"POPULATION_SIZE": ga.POPULATION_SIZE,
            "MUTATION_RATE": ga.MUTATION_RATE,
            "TOURNAMENT_SIZE": ga.TOURNAMENT_SIZE}

VALUES = {"POPULATION_SIZE": [20, 40, 80],
          "MUTATION_RATE": [0.05, 0.1, 0.2],
          "TOURNAMENT_SIZE": [2, 3, 5]}

LABELS = {"POPULATION_SIZE": "population size",
          "MUTATION_RATE": "mutation rate",
          "TOURNAMENT_SIZE": "tournament size"}


def run_key(settings, seed):
    return f"{settings['POPULATION_SIZE']}|{settings['MUTATION_RATE']}|{settings['TOURNAMENT_SIZE']}|{seed}"


def run_once(settings, seed, generations):
    """Run the GA once with these settings. Returns (best per generation, average per generation)."""
    for name, value in settings.items():
        setattr(ga, name, value)          # ga.py reads these names each time it runs
    ga.GENERATIONS = generations
    # ga.py calls crossover() and mutate() without its seeded generator, so they each make
    # an unseeded one and no two runs match. Give them one seeded generator here, so a seed
    # always gives the same run. (If ga.py is changed to pass its own rng to the operators,
    # this still works.)
    operator_rng = np.random.default_rng(seed + 1000)
    # run_ga prints every generation and saves best_chromosome.npy. Silence the printing and
    # block the save, so an experiment never overwrites the saved best.
    with contextlib.redirect_stdout(io.StringIO()), \
            mock.patch("ga.np.save"), \
            mock.patch.object(ga, "crossover", lambda a, b, *_: operators.crossover(a, b, operator_rng)), \
            mock.patch.object(ga, "mutate", lambda c, rate, *_: operators.mutate(c, rate, operator_rng)):
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
                if record["generations"] == generations:
                    runs[run_key(record["settings"], record["seed"])] = record
    return runs


def summarise(runs, generations, out_dir):
    """Print and save one row per setting value, averaged over the seeds."""
    rows = []
    for name, values in VALUES.items():
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


def plot_settings(runs, generations, out_dir):
    """One graph per setting: mean best-fitness curve for each value, with the single runs faint."""
    for name, values in VALUES.items():
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
    parser.add_argument("--generations", type=int, default=ga.GENERATIONS)
    parser.add_argument("--seeds", type=int, default=3, help="seeds per setting (1, 2, 3, ...)")
    parser.add_argument("--out", default="experiment_results")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    runs_path = os.path.join(args.out, "runs.jsonl")
    runs = load_runs(runs_path, args.generations)

    start = time.time()
    for name, values in VALUES.items():
        for value in values:
            settings = dict(DEFAULTS)
            settings[name] = value
            for seed in range(1, args.seeds + 1):
                key = run_key(settings, seed)
                if key in runs:
                    continue          # the default settings appear in every group but run once
                best, average = run_once(settings, seed, args.generations)
                record = {"settings": settings, "seed": seed, "generations": args.generations,
                          "best": best, "average": average}
                runs[key] = record
                with open(runs_path, "a") as f:
                    f.write(json.dumps(record) + "\n")
                print(f"{LABELS[name]} {value}, seed {seed}: final best {best[-1]:.3f} "
                      f"(elapsed {(time.time() - start) / 60:.1f} min)")

    summarise(runs, args.generations, args.out)
    plot_settings(runs, args.generations, args.out)
    print(f"Saved results and graphs in {args.out}/")


if __name__ == "__main__":
    main()
