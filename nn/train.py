"""
nn/train.py - train the network to reproduce the GA's final walking gait.

Run from the main repo folder:  python -m nn.train

Inputs are sin and cos of the step phase, targets are the 24 joint angles scaled 0 to 1
(nn/data.py). Training is stochastic gradient descent: one example at a time, in a new
shuffled order every epoch.
"""

import numpy as np
import matplotlib.pyplot as plt

from nn.network import Network
from nn.data import make_dataset, unscale
from gait import decode

LEARNING_RATE = 0.5
EPOCHS = 2000


def train(inputs, targets, learning_rate=LEARNING_RATE, epochs=EPOCHS, seed=0, verbose=True):
    """Train a fresh [2, 16, 24] network. Returns the network and the mean error of each epoch."""
    net = Network([2, 16, 24], seed=seed)
    rng = np.random.default_rng(seed)
    errors = []
    for epoch in range(epochs):
        # Shuffle each epoch so the network does not learn the frames in one fixed order
        order = rng.permutation(len(inputs))
        errors.append(np.mean([net.train_step(inputs[i], targets[i], learning_rate) for i in order]))
        if verbose and (epoch + 1) % 100 == 0:
            print(f"Epoch {epoch + 1}: error {errors[-1]:.6f}")
    return net, errors


if __name__ == "__main__":
    angles = decode(np.load("final_best_chromosome.npy"))   # the GA's final walking gait
    inputs, targets = make_dataset(angles)

    net, errors = train(inputs, targets)
    assert errors[-1] < errors[0], "error did not fall: try a learning rate of 1.0 or 2.0"
    print(f"Final error: {errors[-1]:.6f}")

    # Training loss. Log scale, because the error drops fast at first and then slowly.
    plt.figure()
    plt.plot(range(1, len(errors) + 1), errors)
    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Mean squared error (scaled angles)")
    plt.title(f"Training loss, learning rate {LEARNING_RATE}")
    plt.grid(True)
    plt.savefig("nn/training_loss.png", dpi=100)

    # Predicted against real angles for one step (frames 0 to 59), L1's three joints
    predicted = unscale(net.forward(inputs))
    frames = np.arange(60)
    plt.figure()
    for joint, name, colour in [(0, "L1 coxa", "tab:blue"), (1, "L1 femur", "tab:orange"), (2, "L1 tibia", "tab:green")]:
        plt.plot(frames, angles[frames, joint], color=colour, label=f"{name} real")
        plt.plot(frames, predicted[frames, joint], color=colour, linestyle="--", label=f"{name} predicted")
    plt.xlabel("Frame")
    plt.ylabel("Angle (rad)")
    plt.title("Predicted (dashed) against real (solid) angles, one step")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.savefig("nn/predicted_vs_real.png", dpi=100)

    net.save("nn/model.npz")
    plt.show()
