
"""
Compare our from-scratch neural network with PyTorch.

Both networks use:
- 2 input, 16 hidden and 24 output neurons
- Sigmoid activation
- Identical starting weights and biases
- The same training data and shuffled example order
- SGD with learning rate 2.0
- Half the sum of squared errors for training
"""

import time
import numpy as np
import torch
import matplotlib.pyplot as plt

from gait import decode
from fitness import score_angles
from nn.data import make_dataset, unscale
from nn.network import Network
from nn.train import train, LEARNING_RATE, EPOCHS


def build_pytorch_model(ours):
    """Build a PyTorch network with our original starting weights."""

    torch.set_default_dtype(torch.float64)

    model = torch.nn.Sequential(
        torch.nn.Linear(2, 16),
        torch.nn.Sigmoid(),
        torch.nn.Linear(16, 24),
        torch.nn.Sigmoid()
    )

    # PyTorch stores weights as outputs x inputs.
    # Our network stores them as inputs x outputs.
    with torch.no_grad():
        model[0].weight.copy_(
            torch.tensor(ours.weights[0].T)
        )
        model[0].bias.copy_(
            torch.tensor(ours.biases[0])
        )
        model[2].weight.copy_(
            torch.tensor(ours.weights[1].T)
        )
        model[2].bias.copy_(
            torch.tensor(ours.biases[1])
        )

    return model


def train_pytorch(model, inputs, targets,
                  learning_rate, epochs, seed=0):
    """Train PyTorch using the same sample order as our network."""

    X = torch.tensor(inputs, dtype=torch.float64)
    Y = torch.tensor(targets, dtype=torch.float64)

    optimizer = torch.optim.SGD(
        model.parameters(), lr=learning_rate
    )

    rng = np.random.default_rng(seed)
    errors = []

    for epoch in range(epochs):
        order = rng.permutation(len(inputs))
        epoch_errors = []

        for i in order:
            optimizer.zero_grad()

            prediction = model(X[i])

            # Match the loss gradient in Network.train_step()
            loss = 0.5 * torch.sum(
                (prediction - Y[i]) ** 2
            )

            # Record mean squared error before the update
            mse = torch.mean(
                (prediction.detach() - Y[i]) ** 2
            ).item()
            epoch_errors.append(mse)

            loss.backward()
            optimizer.step()

        errors.append(np.mean(epoch_errors))

        if (epoch + 1) % 100 == 0:
            print(
                f"PyTorch epoch {epoch + 1}: "
                f"error {errors[-1]:.6f}"
            )

    return np.array(errors)


def compare_weights(ours, model):
    """Return the largest difference in final weights or biases."""

    differences = [
        np.max(np.abs(
            ours.weights[0] -
            model[0].weight.detach().numpy().T
        )),
        np.max(np.abs(
            ours.biases[0] -
            model[0].bias.detach().numpy()
        )),
        np.max(np.abs(
            ours.weights[1] -
            model[2].weight.detach().numpy().T
        )),
        np.max(np.abs(
            ours.biases[1] -
            model[2].bias.detach().numpy()
        ))
    ]

    return max(differences)


def train_pytorch_default(inputs, targets,
                          learning_rate, epochs, seed=0):
    """Train PyTorch with its own initial weights and MSE loss."""

    # Set seed so this experiment is repeatable
    torch.manual_seed(seed)

    model = torch.nn.Sequential(
        torch.nn.Linear(2, 16),
        torch.nn.Sigmoid(),
        torch.nn.Linear(16, 24),
        torch.nn.Sigmoid()
    )

    X = torch.tensor(inputs, dtype=torch.float64)
    Y = torch.tensor(targets, dtype=torch.float64)

    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=learning_rate
    )

    rng = np.random.default_rng(seed)
    errors = []

    start = time.perf_counter()

    for epoch in range(epochs):
        order = rng.permutation(len(inputs))
        epoch_errors = []

        for i in order:
            optimizer.zero_grad()

            prediction = model(X[i])
            loss = criterion(prediction, Y[i])

            epoch_errors.append(loss.item())

            loss.backward()
            optimizer.step()

        errors.append(np.mean(epoch_errors))

    elapsed = time.perf_counter() - start

    with torch.no_grad():
        predictions = model(X).numpy()

    final_mse = np.mean((predictions - targets) ** 2)
    gait_score = score_angles(unscale(predictions))

    return model, np.array(errors), final_mse, elapsed, gait_score


def main():
    seed = 0

    # Load the best gait from the genetic algorithm
    chromosome = np.load("final_best_chromosome.npy")
    angles = decode(chromosome)
    inputs, targets = make_dataset(angles)

    print("Inputs:", inputs.shape)
    print("Targets:", targets.shape)

    # Create identical starting networks
    initial = Network([2, 16, 24], seed=seed)
    model = build_pytorch_model(initial)

    # Train the from-scratch network
    print("\nTraining our network...")

    start = time.perf_counter()

    ours, our_errors = train(
        inputs,
        targets,
        learning_rate=LEARNING_RATE,
        epochs=EPOCHS,
        seed=seed,
        verbose=False
    )

    our_time = time.perf_counter() - start

    # Train the PyTorch network
    print("Training PyTorch network...")

    start = time.perf_counter()

    torch_errors = train_pytorch(
        model,
        inputs,
        targets,
        learning_rate=LEARNING_RATE,
        epochs=EPOCHS,
        seed=seed
    )

    torch_time = time.perf_counter() - start

    # Generate predictions from both networks
    our_predictions = ours.forward(inputs)

    with torch.no_grad():
        torch_predictions = model(
            torch.tensor(inputs, dtype=torch.float64)
        ).numpy()

    # Compare predictions using mean squared error
    our_mse = np.mean(
        (our_predictions - targets) ** 2
    )
    torch_mse = np.mean(
        (torch_predictions - targets) ** 2
    )

    # Convert predictions back into joint angles
    our_angles = unscale(our_predictions)
    torch_angles = unscale(torch_predictions)

    # Score the predicted gaits
    our_fitness = score_angles(our_angles)
    torch_fitness = score_angles(torch_angles)

    # Compare trained parameters
    difference = compare_weights(ours, model)

    print("\n=== COMPARISON RESULTS ===")
    print(f"Our final MSE: {our_mse:.10f}")
    print(f"PyTorch final MSE: {torch_mse:.10f}")

    print(f"Our training time: {our_time:.3f} seconds")
    print(f"PyTorch training time: {torch_time:.3f} seconds")

    print(f"Largest parameter difference: {difference:.10e}")

    print(f"Our gait score: {our_fitness:.6f}")
    print(f"PyTorch gait score: {torch_fitness:.6f}")


    # Second experiment: PyTorch default weights and MSELoss
    print("\nTraining PyTorch with default settings...")

    default_model, default_errors, default_mse, default_time, default_fitness = (
        train_pytorch_default(
            inputs,
            targets,
            learning_rate=LEARNING_RATE,
            epochs=EPOCHS,
            seed=seed
        )
    )

    print("\n=== PYTORCH DEFAULT COMPARISON ===")
    print(f"Final MSE: {default_mse:.10f}")
    print(f"Training time: {default_time:.3f} seconds")
    print(f"Gait score: {default_fitness:.6f}")


    # Plot training errors
    plt.figure(figsize=(9, 5))

    epochs_axis = np.arange(1, len(our_errors) + 1)

    plt.plot(
        epochs_axis, our_errors,
        label="From-scratch network"
    )
    plt.plot(
        epochs_axis, torch_errors,
        label="PyTorch network", linestyle="--"
    )

    plt.plot(
        epochs_axis,
        default_errors,
        label="PyTorch default MSELoss",
        linestyle=":"
    )

    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Mean squared error")
    plt.title("From-Scratch vs PyTorch Training")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(
        "nn/pytorch_comparison.png",
        dpi=150
    )
    plt.show()


if __name__ == "__main__":
    main()
