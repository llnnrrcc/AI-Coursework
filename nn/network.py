import numpy as np
import copy


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
    
def loss(net, inputs, targets):
    """Half the sum of squared errors: the quantity backpropagation computes the gradient of."""
    outputs = net.forward(inputs)
    return 0.5 * np.sum((outputs - np.asarray(targets, dtype=float)) ** 2)


def gradient_check(net, inputs, targets, epsilon=1e-5):
    """Compare backpropagation's gradients with gradients measured by nudging every weight and bias.
    Returns the largest difference found."""
    stepped = copy.deepcopy(net)
    stepped.train_step(inputs, targets, learning_rate=1.0)
    worst = 0.0
    for layer in range(len(net.weights)):
        pairs = [(net.weights[layer], net.weights[layer] - stepped.weights[layer]),
                 (net.biases[layer], net.biases[layer] - stepped.biases[layer])]
        for params, backprop in pairs:
            for index in np.ndindex(params.shape):
                original = params[index]
                params[index] = original + epsilon
                loss_up = loss(net, inputs, targets)
                params[index] = original - epsilon
                loss_down = loss(net, inputs, targets)
                params[index] = original
                measured = (loss_up - loss_down) / (2 * epsilon)
                worst = max(worst, abs(measured - backprop[index]))
    return worst


if __name__ == "__main__":
    net = Network([2, 16, 24])
    print("gradient check, 1 hidden layer:", gradient_check(net, [0.0, 1.0], np.linspace(0.2, 0.8, 24)))
    net = Network([2, 16, 16, 24], seed=3)
    print("gradient check, 2 hidden layers:", gradient_check(net, [0.3, -0.9], np.linspace(0.8, 0.1, 24)))