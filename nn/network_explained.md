# How the network works (`nn/network.py`)

`network.py` is a fully connected neural network written from scratch with NumPy, following the structure of Practical 5 (`Full_NN`). No neural network library is used. The final network is [2, 16, 24]: 2 inputs, one hidden layer of 16 neurons, and 24 outputs (the size is justified in `architectures.md`).

## What goes in and what comes out

The input is where the spider is in its step, given as two numbers: the sine and cosine of the step phase. The output is the 24 joint angles for that moment, each scaled to between 0 and 1 using that joint's limits, then turned back into real angles afterwards (`data.py`). Training adjusts the network until its outputs match the GA's final gait.

## Weights, biases and starting values

Every connection between two neurons has a weight: how strongly one neuron affects the next. Every neuron also has a bias: an extra number added to its total, so it can shift its output up or down even when its inputs are zero. Practical 5 has no bias; we added one to every layer, as in the module's worked backpropagation equations, because without it every neuron's curve is forced through the same point.

Weights start as random numbers between -0.5 and 0.5, and biases start at 0. Practical 5 starts weights between 0 and 1. Allowing negative starting weights means neurons don't all begin pushing in the same direction, which usually trains faster and more evenly. The random start is seeded, so the same seed always gives the same network.

## The forward pass: producing an answer

For each layer, every neuron:

1. multiplies each input by its weight and adds them up,
2. adds its bias,
3. squashes the total with the sigmoid function, which turns any number into one between 0 and 1.

    a = sigmoid(x × W + b),   where sigmoid(z) = 1 / (1 + e^(-z))

The hidden layer's outputs become the output layer's inputs. The output layer's 24 values are the network's answer. Sigmoid suits the output because the targets are scaled to between 0 and 1, so every predicted angle is guaranteed to stay inside its joint's limits.

The whole layer is calculated at once with one matrix multiplication (`x @ W + b`) instead of a loop over neurons. The same code works for one example or for all 300 frames at once, which is how the graphs are made quickly.

## The error

The network predicts 24 joint angles, which are continuous numbers rather than categories, so this is a regression problem. The usual loss for regression is the mean squared error (MSE), and it suits our problem for three reasons.

Squaring each difference means a big error counts for much more than a small one. This matters for a walking gait, because one angle that is badly wrong can push a foot through the floor or lift it off the ground, while lots of tiny errors make almost no difference to the walk. MSE also has a simple gradient. With the sigmoid output, the error signal for each output neuron is just (output - target) × output × (1 - output), which is the first step of backpropagation below. Finally, a loss like cross-entropy is built for predicting classes, so it does not fit targets that are angles.

During training, the error for one example is half the sum of the squared differences between the outputs and the targets. The half cancels when the error is differentiated, which keeps the backpropagation equations simple. The graphs report the mean squared error instead, which is easier to compare between runs.

## Backpropagation: learning from the error

Backpropagation works out how much each weight and bias contributed to the error, starting at the output and working backwards.

1. **Output layer.** For each output neuron, `delta = (output - target) × output × (1 - output)`. The first part is how wrong the output is. The second part, `output × (1 - output)`, is the slope of the sigmoid at that point: how much the output would change if the neuron's total changed.
2. **Weight gradients.** Each weight's share of the blame is the input that came through it multiplied by the delta of the neuron it feeds.
3. **Hidden layer.** The output deltas are sent backwards through the same weights, then multiplied by the hidden neurons' own sigmoid slopes, giving each hidden neuron its delta.
4. **Update.** Every weight and bias moves a small step against its gradient: `new = old - learning rate × gradient`.

This is stochastic gradient descent: the weights are updated after every single example, with the 300 frames shuffled into a new order every epoch (`train.py`). The learning rate is 2.0, chosen by comparing four rates (`training.md`).

## Proving backpropagation is correct: the gradient check

A falling error shows the network is learning, but not that the backpropagation maths is exactly right. The gradient check proves it. For every single weight and bias, it nudges the value up by a tiny amount (0.00001), measures the error, nudges it down by the same amount, measures again, and works out the slope from those two errors. That measured slope is then compared with the gradient backpropagation calculated.

The largest difference across every weight and bias was 0.00000000001 (about 1e-11) with one hidden layer, and the same with two hidden layers. Backpropagation agrees with the measured gradients to about 11 decimal places. Run it with `python -m nn.network`.

## Sigmoid and vanishing gradients

The sigmoid's slope is at most 0.25, and it gets very close to 0 when a neuron's total is very large or very small. Because each layer's delta is multiplied by that slope, deltas shrink as they travel backwards through many layers, so early layers learn very slowly. This is the vanishing gradient problem. With one hidden layer it does not cause trouble here, and the two-hidden-layer network still trained well, but it is one reason deep networks usually use other activations such as ReLU.

The sigmoid also never quite reaches 0 or 1. When a joint sits exactly at its limit, its target is exactly 0 or 1, so the network can only get close. This is where its largest errors are (`training.md`).

## Saving and loading

`net.save("nn/model.npz")` stores the layer sizes, weights and biases in one NumPy file. `Network.load("nn/model.npz")` rebuilds the same network from it. A test in `network.py` checks that a loaded network gives exactly the same outputs as the original. `nn/model.npz` is the saved final model the brief asks for.

