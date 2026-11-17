"""
nn/architectures.py - train networks of different sizes and compare them.

Run from the main repo folder:  python -m nn.architectures

Every network uses the same data, learning rate (2.0), epochs (2,000) and seed, so only the
layer sizes differ. Each is compared on final error, training time and the fitness of the
gait it produces.
"""

import time

import numpy as np
import matplotlib.pyplot as plt

from nn.train import train
from nn.data import make_dataset, unscale
from gait import decode
from fitness import score_angles

ARCHITECTURES = [
    [2, 2, 24],
    [2, 4, 24],
    [2, 8, 24],
    [2, 16, 24],
    [2, 32, 24],
    [2, 16, 16, 24],
]

if __name__ == "__main__":
    inputs, targets = make_dataset(decode(np.load("final_best_chromosome.npy")))

    plt.figure()
    print(f"{'layers':16} {'weights':>8} {'final error':>12} {'time (s)':>9} {'gait fitness':>13}")
    for sizes in ARCHITECTURES:
        start = time.perf_counter()
        net, errors = train(inputs, targets, verbose=False, layer_sizes=sizes)
        seconds = time.perf_counter() - start
        n_weights = sum(w.size + b.size for w, b in zip(net.weights, net.biases))
        gait_fitness = score_angles(unscale(net.forward(inputs)))
        print(f"{str(sizes):16} {n_weights:8d} {errors[-1]:12.7f} {seconds:9.1f} {gait_fitness:13.3f}")
        plt.plot(range(1, len(errors) + 1), errors, label=f"{sizes} (final {errors[-1]:.1e})")

    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Mean squared error (scaled angles)")
    plt.title("Training loss by network size")
    plt.legend(title="Layer sizes")
    plt.grid(True)
    plt.savefig("nn/architectures.png", dpi=100)
    plt.show()