"""
foot_heights.py - graph how high each foot is through one step.

Run from inside the AI-Coursework folder:
    python foot_heights.py

This is the graph that shows leg faults the fitness score hides: a foot that never
comes down to the floor (hovering) or that drops under it instead of lifting (sinking).
The floor band from DECISIONS.md is shaded, so a healthy foot dips into the band
(planted) and rises clearly above it (lifting).

Only the left legs are drawn. Each right leg copies its left partner half a step later,
so it has the same heights, shifted.

Running this file saves the graphs for the two earlier runs used in the write-up
(visualisation.md). Their best chromosomes are kept in results/earlier_runs/, because
the code that made them has since changed:
    sinking_best.npy    seed 42, population 40, fitness before commit fbc58bd
    hovering_best.npy   seed 42, population 40, fitness after fbc58bd, before e239a78
save_results.py uses plot_foot_heights() for the final gait.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fitness import feet_positions, FLOOR, BAND_LOW, BAND_HIGH
from gait import decode, N_FRAMES, N_CYCLES

STEP_FRAMES = N_FRAMES // N_CYCLES      # 60 frames = one step
LEFT_LEGS = ["L1", "L2", "L3", "L4"]     # positions 0-3 in the foot order


def plot_foot_heights(angles, title, path):
    """Save a graph of each left foot's height (z) over the first step of `angles`."""
    feet_z = feet_positions(angles[:STEP_FRAMES], frame_step=1)[:, :, 2]   # (60, 8)
    frames = np.arange(1, STEP_FRAMES + 1)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.axhspan(BAND_LOW, BAND_HIGH, color="tab:green", alpha=0.15, label="Touching the floor")
    ax.axhline(FLOOR, color="grey", linewidth=1)
    for leg, name in enumerate(LEFT_LEGS):
        ax.plot(frames, feet_z[:, leg], linewidth=2, label=name)
    ax.set_xlabel("Frame (one step)")
    ax.set_ylabel("Foot height z")
    ax.set_title(title)
    ax.set_xlim(1, STEP_FRAMES)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return feet_z


if __name__ == "__main__":
    folder = os.path.join("results", "earlier_runs")
    runs = [("sinking_best.npy", "Before the sinking fix: L2 and L4 dip under the band",
             "foot_heights_sinking.png"),
            ("hovering_best.npy", "After the sinking fix: L2 never touches the floor",
             "foot_heights_hovering.png")]
    for file_name, title, png in runs:
        angles = decode(np.load(os.path.join(folder, file_name)))
        feet_z = plot_foot_heights(angles, title, os.path.join(folder, png))
        print(f"{file_name}: saved {png}")
        for leg, name in enumerate(LEFT_LEGS):
            print(f"  {name}: lowest {feet_z[:, leg].min():+.3f}, highest {feet_z[:, leg].max():+.3f}")
