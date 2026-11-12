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
    
    def train_step(self, inputs, targets, learning_rate):
        """Learn from one example: forward pass, backpropagation, then gradient descent. Returns the squared error."""
        outputs = self.forward(inputs)
        targets = np.asarray(targets, dtype=float)

        # Output layer: the error, times the slope of sigmoid at each output
        delta = (outputs - targets) * outputs * (1 - outputs)

        # Work backwards through the layers
        for layer in reversed(range(len(self.weights))):
            layer_input = self.activations[layer]
            weight_gradient = np.outer(layer_input, delta)
            bias_gradient = delta

            # Pass the blame back to the previous layer, using the weights before they change
            if layer > 0:
                delta = (delta @ self.weights[layer].T) * layer_input * (1 - layer_input)

            # Gradient descent: step each weight against its gradient
            self.weights[layer] -= learning_rate * weight_gradient
            self.biases[layer] -= learning_rate * bias_gradient

        return float(np.mean((outputs - targets) ** 2))


if __name__ == "__main__":
    net = Network([2, 16, 24])
    inputs = [0.0, 1.0]
    targets = np.linspace(0.2, 0.8, 24)
    print("error before:", round(net.train_step(inputs, targets, 0.5), 5))
    for _ in range(1000):
        error = net.train_step(inputs, targets, 0.5)
    print("error after 1000 steps:", round(error, 5))