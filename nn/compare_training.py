"""
nn/compare_training.py - compare hidden-layer activations and batch sizes for the network.

Run from the main repo folder:  python -m nn.compare_training
Quick test:                     python -m nn.compare_training --epochs 50 --seeds 1

Two comparisons, both on the [2, 16, 24] network and the final GA gait:
  1. Hidden activation: sigmoid (ours), tanh and ReLU, trained one example at a time.
     The output layer stays sigmoid, so every predicted angle stays inside its joint limits.
  2. Batch size: 1 (ours), 10, 30 and 300 (the whole step), with a sigmoid hidden layer.
     A batch updates the weights once with the average gradient of its examples.
A learning rate that suits one setting can be wrong for another, so each setting is trained
at three learning rates and the best one is reported. Every setting is repeated over several
seeds (starting weights and shuffle order).

Sigmoid with batch size 1 is exactly the training in nn/train.py, so its learning rate 2.0,
seed 0 run reproduces nn/model.npz.

Saves nn/compare_training.csv (every run), nn/activations.png and nn/batch_sizes.png.
"""

import argparse
import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from nn.network import Network, gradient_check
from nn.data import make_dataset, unscale
from gait import decode
from fitness import score_angles

ACTIVATIONS = ["sigmoid", "tanh", "relu"]
ACTIVATION_RATES = [0.1, 0.5, 2.0]
BATCH_SIZES = [1, 10, 30, 300]
BATCH_RATES = [0.5, 2.0, 8.0]


class FlexibleNetwork(Network):
    """The same network as nn/network.py, with a choice of hidden activation and batch training.
    The output layer is always sigmoid. With hidden="sigmoid" it behaves exactly like Network."""

    def __init__(self, layer_sizes, seed=0, hidden="sigmoid"):
        super().__init__(layer_sizes, seed)
        self.hidden = hidden

    def activate(self, x, output_layer):
        if output_layer or self.hidden == "sigmoid":
            return self.sigmoid(x)
        if self.hidden == "tanh":
            return np.tanh(x)
        return np.maximum(0.0, x)   # relu

    def slope(self, a):
        """The activation's slope, worked out from its output a."""
        if self.hidden == "sigmoid":
            return a * (1 - a)
        if self.hidden == "tanh":
            return 1 - a ** 2
        return (a > 0).astype(float)   # relu

    def forward(self, inputs):
        self.activations = [np.asarray(inputs, dtype=float)]
        last = len(self.weights) - 1
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            self.activations.append(self.activate(self.activations[-1] @ w + b, i == last))
        return self.activations[-1]

    def train_step(self, inputs, targets, learning_rate):
        """One example or a batch (one row per example): forward pass, backpropagation, then one
        update with the gradient averaged over the batch. Returns the mean squared error."""
        outputs = self.forward(inputs)
        targets = np.asarray(targets, dtype=float)
        batch = 1 if outputs.ndim == 1 else len(outputs)
        delta = (outputs - targets) * outputs * (1 - outputs)   # output layer is always sigmoid
        for layer in reversed(range(len(self.weights))):
            layer_input = self.activations[layer]
            if outputs.ndim == 1:
                weight_gradient, bias_gradient = np.outer(layer_input, delta), delta
            else:
                weight_gradient, bias_gradient = layer_input.T @ delta / batch, delta.mean(axis=0)
            if layer > 0:
                delta = (delta @ self.weights[layer].T) * self.slope(layer_input)
            self.weights[layer] -= learning_rate * weight_gradient
            self.biases[layer] -= learning_rate * bias_gradient
        return float(np.mean((outputs - targets) ** 2))


def run(job):
    """Train one network. job = (hidden, batch_size, learning_rate, seed, epochs)."""
    hidden, batch_size, rate, seed, epochs = job
    inputs, targets = make_dataset(decode(np.load("final_best_chromosome.npy")))
    net = FlexibleNetwork([2, 16, 24], seed=seed, hidden=hidden)
    rng = np.random.default_rng(seed)
    curve = []
    start = time.time()
    for _ in range(epochs):
        order = rng.permutation(len(inputs))   # same shuffle as nn/train.py
        if batch_size == 1:
            for i in order:
                net.train_step(inputs[i], targets[i], rate)
        else:
            for k in range(0, len(order), batch_size):
                chunk = order[k:k + batch_size]
                net.train_step(inputs[chunk], targets[chunk], rate)
        outputs = net.forward(inputs)
        curve.append(float(np.mean((outputs - targets) ** 2)))
    seconds = time.time() - start
    error = curve[-1]
    gait = score_angles(unscale(net.forward(inputs))) if np.isfinite(error) else float("nan")
    return {"hidden": hidden, "batch_size": batch_size, "learning_rate": rate, "seed": seed,
            "final_error": error, "gait_fitness": gait, "seconds": seconds, "curve": curve}


def best_rate(results, hidden, batch_size, rates):
    """The learning rate (out of rates) with the lowest mean final error for this setting, and its runs."""
    best = None
    for rate in rates:
        runs = [r for r in results if (r["hidden"], r["batch_size"], r["learning_rate"]) == (hidden, batch_size, rate)]
        errors = [r["final_error"] for r in runs]
        mean = np.mean(errors) if all(np.isfinite(errors)) else np.inf
        if best is None or mean < best[0]:
            best = (mean, rate, runs)
    return best


def report(results, settings, rates, title, filename, label):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    print(f"\n{title}")
    print(f"{'setting':>10s} {'best rate':>9s} {'final error (mean +- sd)':>26s} {'worst seed':>11s} "
          f"{'gait fitness':>12s} {'seconds':>8s}")
    plt.figure(figsize=(8, 5))
    for hidden, batch_size in settings:
        mean, rate, runs = best_rate(results, hidden, batch_size, rates)
        errors = np.array([r["final_error"] for r in runs])
        name = label(hidden, batch_size)
        print(f"{name:>10s} {rate:9.1f} {errors.mean():14.7f} +- {errors.std():.7f} {errors.max():11.7f} "
              f"{np.mean([r['gait_fitness'] for r in runs]):12.3f} {np.mean([r['seconds'] for r in runs]):8.1f}")
        curve = np.mean([r["curve"] for r in runs], axis=0)
        plt.plot(range(1, len(curve) + 1), curve, label=f"{name} (rate {rate}, final {errors.mean():.1e})")
    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Mean squared error (scaled angles)")
    plt.title(f"{title} (best learning rate each, mean of {len(runs)} seeds)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Compare hidden activations and batch sizes.")
    parser.add_argument("--epochs", type=int, default=2000)
    parser.add_argument("--seeds", type=int, default=3, help="seeds 0, 1, 2, ...")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    args = parser.parse_args()

    # Check the new backpropagation first: it must match measured gradients like nn/network.py does
    for hidden in ACTIVATIONS:
        net = FlexibleNetwork([2, 16, 24], seed=1, hidden=hidden)
        print(f"gradient check, {hidden} hidden layer: {gradient_check(net, [0.3, -0.9], np.linspace(0.2, 0.8, 24)):.1e}")

    jobs = {(h, 1, rate, s, args.epochs) for h in ACTIVATIONS for rate in ACTIVATION_RATES for s in range(args.seeds)}
    jobs |= {("sigmoid", b, rate, s, args.epochs) for b in BATCH_SIZES for rate in BATCH_RATES for s in range(args.seeds)}
    print(f"{len(jobs)} training runs on {args.workers} workers")
    start = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run, sorted(jobs)))
    print(f"done in {(time.time() - start) / 60:.1f} min")

    with open("nn/compare_training.csv", "w", newline="") as f:
        fields = ["hidden", "batch_size", "learning_rate", "seed", "final_error", "gait_fitness", "seconds"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in fields})

    report(results, [(h, 1) for h in ACTIVATIONS], ACTIVATION_RATES, "Hidden activation", "nn/activations.png",
           lambda h, b: h)
    report(results, [("sigmoid", b) for b in BATCH_SIZES], BATCH_RATES, "Batch size", "nn/batch_sizes.png",
           lambda h, b: f"batch {b}")
    print("\nSaved nn/compare_training.csv, nn/activations.png and nn/batch_sizes.png")


if __name__ == "__main__":
    main()
