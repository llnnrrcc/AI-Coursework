"""
nn/show_nn_gait.py - animate the trained network's gait and score it against the GA's.

Run from the main repo folder:  python -m nn.show_nn_gait

The network gets the 300 step phases as input and outputs 24 joint angles for each. Those
angles are animated and scored with the same fitness function as the GA, so the two gaits
can be compared directly.
"""

import numpy as np

from nn.network import Network
from nn.data import make_dataset, unscale
from gait import decode, animate
from fitness import fitness, score_angles

if __name__ == "__main__":
    ga_best = np.load("final_best_chromosome.npy")
    ga_angles = decode(ga_best)
    inputs, _ = make_dataset(ga_angles)

    net = Network.load("nn/model.npz")
    nn_angles = unscale(net.forward(inputs))

    error = np.abs(nn_angles - ga_angles)
    print(f"GA gait fitness:      {fitness(ga_best):.3f}")
    print(f"Network gait fitness: {score_angles(nn_angles):.3f}")
    print(f"Angle error: mean {error.mean():.4f} rad, worst {error.max():.4f} rad")

    animate(nn_angles)