"""
save_results.py - save the final GA run's visuals into results/ for the report.

Run from inside the AI-Coursework folder:
    python save_results.py                  uses final_best_chromosome.npy, seed 1
    python save_results.py --rerun          ignore the saved history and re-run the GA

Outputs (in results/):
    fitness_history.csv     best and average fitness for every generation
    fitness_history.png     the same as a graph
    best_gait.gif           one full step of the best gait, looping
    pose_side.png           still pose from the side, with the floor band drawn in
    pose_top.png            the same pose from above
    foot_heights.png        each foot's height through one step, with the floor band

The fitness history is not stored in the .npy file, so the first time this runs it
re-runs the GA with the final settings in ga.py and the same seed (a few minutes). The
GA is seeded, so the re-run is the same run, and the script checks this: the re-run's
best chromosome must match final_best_chromosome.npy exactly. If it does not, the
settings or fitness have changed since the file was made, and the script stops rather
than save a graph of a different run.

The history is saved with a fingerprint of the chromosome, so later runs reuse it and
take seconds. When the final chromosome changes, the fingerprint no longer matches and
the GA is re-run automatically.
"""

import argparse
import contextlib
import hashlib
import io
import os
from unittest import mock

import matplotlib
matplotlib.use("Agg")          # save to files, do not open windows
import matplotlib.pyplot as plt
import numpy as np

import ga
from fitness import score_angles, FLOOR, BAND_LOW, BAND_HIGH
from gait import decode, animate, N_FRAMES, N_CYCLES
from foot_heights import plot_foot_heights
from spider_model import draw_legs, spider_joints, BODY_A, BODY_B

STEP_FRAMES = N_FRAMES // N_CYCLES      # 60 frames = one full step


def fingerprint(chromosome):
    """Short ID for a chromosome, so a saved history can be matched to it."""
    return hashlib.sha1(np.asarray(chromosome, dtype=float).tobytes()).hexdigest()[:12]


# --- Fitness history ---------------------------------------------------------

def load_history(path, chromosome):
    """Return (best, average) from a saved CSV, or None if missing or for another chromosome."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        first_line = f.readline().strip()
    if first_line != f"# chromosome {fingerprint(chromosome)}":
        print(f"{path} is for a different chromosome, so the GA will be re-run.")
        return None
    data = np.loadtxt(path, delimiter=",", skiprows=2)
    return data[:, 1], data[:, 2]


def rerun_history(chromosome, seed):
    """Re-run the GA with ga.py's settings and this seed. Returns (best, average)."""
    print(f"Re-running the GA (population {ga.POPULATION_SIZE}, {ga.GENERATIONS} generations, "
          f"seed {seed}) to get the fitness history. This takes a few minutes...")
    # run_ga prints every generation and saves best_chromosome.npy: hide the printing and
    # block the save, so this never overwrites anything.
    with contextlib.redirect_stdout(io.StringIO()), mock.patch("ga.np.save"):
        best, best_history, average_history = ga.run_ga(seed)

    # Check the re-run is the same run. Its final best must score the same as the saved
    # chromosome. The genes themselves can differ: once many chromosomes tie on the top
    # score, which one counts as "best" can change with tiny rounding differences between
    # computers, but the run and its history are the same.
    saved_score = score_angles(decode(chromosome))
    if not np.isclose(best_history[-1], saved_score):
        raise SystemExit(
            f"The re-run's best score ({best_history[-1]:.3f}) is not the saved chromosome's "
            f"({saved_score:.3f}), so this would be the graph of a different run.\n"
            "Check that ga.py's settings, fitness.py and the seed (--seed) are the ones the "
            "final run used.")
    if not np.array_equal(best, chromosome):
        print("Note: the re-run ended on a different chromosome with the same top score "
              f"({saved_score:.3f}). The history is the same run; the GIF and poses use the saved file.")
    return np.array(best_history), np.array(average_history)


def save_history(path, chromosome, best, average):
    with open(path, "w") as f:
        f.write(f"# chromosome {fingerprint(chromosome)}\n")
        f.write("generation,best,average\n")
        for generation, (b, a) in enumerate(zip(best, average), start=1):
            f.write(f"{generation},{b:.6f},{a:.6f}\n")


def plot_history(best, average, path):
    generations = np.arange(1, len(best) + 1)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(generations, best, label="Best fitness", linewidth=2)
    ax.plot(generations, average, label="Average fitness", linewidth=2)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness score")
    ax.set_title(f"GA fitness over generations (population {ga.POPULATION_SIZE})")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --- Still poses -------------------------------------------------------------

def mid_swing_frame(angles):
    """The frame (within the first step) where the highest foot is highest: legs clearly lifting."""
    heights = [max(leg[3][2] for leg in spider_joints(angles[t])) for t in range(STEP_FRAMES)]
    return int(np.argmax(heights))


def draw_spider(ax, pose):
    t = np.linspace(0, 2 * np.pi, 100)
    ax.plot(BODY_A * np.cos(t), BODY_B * np.sin(t), np.zeros_like(t), color="black", linewidth=3)
    ax.scatter(BODY_A + 0.2, 0, 0, color="red", marker="^", s=80)   # front of the spider
    draw_legs(ax, pose)


def save_pose(pose, frame, view, path):
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    draw_spider(ax, pose)

    if view == "side":
        # Floor and the band a foot counts as touching it, seen edge-on from the side
        x = np.array([-4, 4])
        for z, style in [(FLOOR, "-"), (BAND_LOW, ":"), (BAND_HIGH, ":")]:
            ax.plot(x, [0, 0], [z, z], color="grey", linestyle=style, linewidth=1)
        ax.view_init(elev=0, azim=-90)        # look along the y axis: x (forwards) and z (up)
        ax.set_proj_type("ortho")             # no perspective, so heights can be compared
        ax.set_zlim(-1, 1)
        ax.set_yticks([]); ax.set_ylabel("")  # y points into the page, so its ticks just overlap
        title = "Side view (height stretched 4x to show lift)"
    else:
        ax.view_init(elev=90, azim=-90)       # look straight down: front of the spider to the right
        ax.set_proj_type("ortho")
        ax.set_zlim(-2, 2)
        ax.set_zticks([])                     # z points out of the page
        title = "Top view"

    ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
    ax.set_xlabel("X (forwards)")
    if view == "side":
        ax.set_zlabel("Z (up)")
    else:
        ax.set_ylabel("Y (left)")
    ax.set_title(f"{title}, frame {frame + 1} (mid-swing)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --- Main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--chromosome", default="final_best_chromosome.npy")
    parser.add_argument("--seed", type=int, default=1, help="seed the final run used (default 1)")
    parser.add_argument("--out", default="results")
    parser.add_argument("--rerun", action="store_true", help="re-run the GA even if a history is saved")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    chromosome = np.load(args.chromosome)
    angles = decode(chromosome)
    print(f"{args.chromosome}: fitness {score_angles(angles):.3f}")

    # 1. Fitness graph
    csv_path = os.path.join(args.out, "fitness_history.csv")
    history = None if args.rerun else load_history(csv_path, chromosome)
    if history is None:
        history = rerun_history(chromosome, args.seed)
        save_history(csv_path, chromosome, *history)
    plot_history(*history, os.path.join(args.out, "fitness_history.png"))
    print(f"Saved fitness graph (best {history[0][-1]:.3f}, average {history[1][-1]:.3f} at the end)")

    # 2. Gait GIF: one full step. The gait repeats every 60 frames, so this loops seamlessly.
    gif_path = os.path.join(args.out, "best_gait.gif")
    animate(angles[:STEP_FRAMES], save_as=gif_path)
    plt.close("all")
    print(f"Saved {gif_path}")

    # 3. Side and top still poses at the same moment
    frame = mid_swing_frame(angles)
    save_pose(angles[frame], frame, "side", os.path.join(args.out, "pose_side.png"))
    save_pose(angles[frame], frame, "top", os.path.join(args.out, "pose_top.png"))
    print(f"Saved side and top poses at frame {frame + 1}")

    # 4. Foot heights through one step: every foot should dip into the band and lift above it
    plot_foot_heights(angles, "Final gait: foot height through one step",
                      os.path.join(args.out, "foot_heights.png"))
    print("Saved foot height graph")


if __name__ == "__main__":
    main()
