"""
nn/learning_rates.py - train with three learning rates and compare the error curves.

Run from the main repo folder:  python -m nn.learning_rates

Every run uses the same seed, so the starting weights and the shuffle order are identical
and only the learning rate differs.
"""

import numpy as np
import matplotlib.pyplot as plt

from nn.train import train
from nn.data import make_dataset
from gait import decode

# 30.0 is there to show what too high looks like: in a test it stalled above its starting error
RATES = [0.1, 0.5, 2.0, 30.0]

if __name__ == "__main__":
    inputs, targets = make_dataset(decode(np.load("final_best_chromosome.npy")))

    plt.figure()
    for rate in RATES:
        _, errors = train(inputs, targets, learning_rate=rate, verbose=False)
        print(f"Learning rate {rate}: error after epoch 100 {errors[99]:.6f}, final {errors[-1]:.6f}")
        plt.plot(range(1, len(errors) + 1), errors, label=f"{rate} (final {errors[-1]:.1e})")
    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Mean squared error (scaled angles)")
    plt.title("Training loss by learning rate")
    plt.legend(title="Learning rate")
    plt.grid(True)
    plt.savefig("nn/learning_rates.png", dpi=100)
    plt.show()
