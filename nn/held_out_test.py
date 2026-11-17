"""
nn/held_out_test.py - check the network has learned the gait, not memorised the frames.

Run from the main repo folder:  python -m nn.held_out_test

The gait repeats every 60 frames, so the 300 training examples are only 60 different
moments. Here a fresh network is trained on the even frames only (30 of the 60 moments),
then tested on the odd frames, which it never saw. If the error on the unseen frames is
about the same as on the training frames, the network has learned the smooth shape of each
joint's movement rather than a lookup table of the frames it was shown.
"""

import numpy as np
import matplotlib.pyplot as plt

from nn.train import train
from nn.data import make_dataset, unscale
from gait import decode
from fitness import score_angles

if __name__ == "__main__":
    angles = decode(np.load("final_best_chromosome.npy"))
    inputs, targets = make_dataset(angles)

    seen = np.arange(0, 300, 2)      # even frames: used for training
    unseen = np.arange(1, 300, 2)    # odd frames: never shown to the network

    net, _ = train(inputs[seen], targets[seen], verbose=False)

    seen_error = np.mean((net.forward(inputs[seen]) - targets[seen]) ** 2)
    unseen_error = np.mean((net.forward(inputs[unseen]) - targets[unseen]) ** 2)
    predicted = unscale(net.forward(inputs))
    angle_error = np.abs(predicted[unseen] - angles[unseen])

    print(f"Error on training frames (seen):   {seen_error:.7f}")
    print(f"Error on held-out frames (unseen): {unseen_error:.7f}")
    print(f"Unseen frames, angle error: mean {angle_error.mean():.4f} rad, worst {angle_error.max():.4f} rad")
    print(f"Gait fitness of the full 300 frames: {score_angles(predicted):.3f}")

    # One joint over one step: training frames as dots, unseen frames as crosses
    frames = np.arange(60)
    plt.figure()
    plt.plot(frames, angles[:60, 0], "k-", label="real (L1 coxa)")
    plt.plot(frames[::2], predicted[:60:2, 0], "o", label="predicted, seen frames")
    plt.plot(frames[1::2], predicted[1:60:2, 0], "x", label="predicted, unseen frames")
    plt.xlabel("Frame")
    plt.ylabel("Angle (rad)")
    plt.title("Held-out test: trained on even frames, tested on odd")
    plt.legend()
    plt.grid(True)
    plt.savefig("nn/held_out_test.png", dpi=100)
    plt.show()