"""
nn/size_check.py - is a network accurate enough? Checks foot positions, not just error.

Run from the main repo folder:  python -m nn.size_check

The fitness decides whether a foot is touching the floor by a hard line (z = -0.25), and
the GA's gait lifts its feet only just above that line. So the size that matters is how
far the network's feet end up from the GA's feet, and whether any foot ends up on the
wrong side of the line. Each size is trained on 3 seeds so one lucky run can't decide it.
"""

import numpy as np

from nn.train import train
from nn.data import make_dataset, unscale
from gait import decode
from fitness import feet_positions, score_angles, BAND_HIGH

SIZES = [[2, 8, 24], [2, 16, 24], [2, 32, 24]]
SEEDS = [0, 1, 2]

if __name__ == "__main__":
    angles = decode(np.load("final_best_chromosome.npy"))
    inputs, targets = make_dataset(angles)
    ga_feet = feet_positions(angles)
    ga_touching = ga_feet[:, :, 2] <= BAND_HIGH

    print(f"GA gait fitness: {score_angles(angles):.3f}\n")
    print(f"{'layers':12} {'seed':>4} {'error':>10} {'worst foot height error':>24} {'feet on wrong side':>19} {'gait fitness':>13}")
    for sizes in SIZES:
        for seed in SEEDS:
            net, errors = train(inputs, targets, verbose=False, layer_sizes=sizes, seed=seed)
            predicted = unscale(net.forward(inputs))
            feet = feet_positions(predicted)
            worst = np.abs(feet[:, :, 2] - ga_feet[:, :, 2]).max()
            wrong_side = np.sum((feet[:, :, 2] <= BAND_HIGH) != ga_touching)
            print(f"{str(sizes):12} {seed:4d} {errors[-1]:10.7f} {worst:24.4f} {wrong_side:19d} {score_angles(predicted):13.3f}")
        print()