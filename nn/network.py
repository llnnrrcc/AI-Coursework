import numpy as np


class Network:

    def __init__(self, layer_sizes, seed=0):
        """layer_sizes lists the neurons in each layer, e.g. [2, 16, 24]: 2 inputs, 16 hidden, 24 outputs."""
        rng = np.random.default_rng(seed)
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []
        for n_in, n_out in zip(layer_sizes[:-1], layer_sizes[1:]):
            self.weights.append(rng.uniform(-0.5, 0.5, size=(n_in, n_out)))
            self.biases.append(np.zeros(n_out))

    def sigmoid(self, x):
        """Squash any number into the range 0 to 1."""
        return 1.0 / (1.0 + np.exp(-x))

    def forward(self, inputs):
        """Run the inputs through every layer and return the outputs. Keeps each layer's output for backpropagation."""
        self.activations = [np.asarray(inputs, dtype=float)]
        for w, b in zip(self.weights, self.biases):
            self.activations.append(self.sigmoid(self.activations[-1] @ w + b))
        return self.activations[-1]


if __name__ == "__main__":
    net = Network([2, 16, 24])
    for w, b in zip(net.weights, net.biases):
        print(w.shape, b.shape)
    outputs = net.forward([0.0, 1.0])
    print(outputs.shape, round(outputs.min(), 3), round(outputs.max(), 3))