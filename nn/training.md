# Neural network training (Part 2)

## What the network learns

The network learns to reproduce the GA's final walking gait (`final_best_chromosome.npy`: population 80, seed 1, 100 generations, fitness 2.227 with the energy term and per-leg forward scoring). Earlier versions of this write-up used the GA's previous final gaits; all numbers below are for the current one. Given where the spider is in its step, it outputs all 24 joint angles for that moment.

## Training data

`nn/data.py` builds the data from the GA's gait: `decode()` turns the chromosome into 300 frames of 24 joint angles, and each frame becomes one example.

- Inputs: 2 numbers per frame, the sine and cosine of the step phase (2π × 5 × frame / 300, since there are 5 steps in 300 frames). Using both puts the phase on a circle, so the last frame of a step sits next to the first, and no two points in the step get the same input. Sine alone would give the same value twice per step.
- Targets: the 24 joint angles, each scaled to 0 to 1 using that joint's limits (right-leg coxa limits are the left ones mirrored). The output layer uses sigmoid, which only produces 0 to 1, so the targets have to be in that range. Scaling every joint by its own limits also gives each joint equal weight in the error, so the tibia (range 1.7 rad) does not drown out a coxa with a range of 0.33 rad.
- `unscale()` turns outputs back into angles. Because a sigmoid output can never leave 0 to 1, every predicted angle is guaranteed to be inside its joint's limits.

The gait repeats every 60 frames, so the 300 examples are 60 different moments, each seen 5 times.

## Network

`nn/network.py`, written from scratch in NumPy: layers [2, 16, 24], so 2 inputs, 16 hidden neurons and 24 outputs, sigmoid in every layer. Weights start as random numbers between -0.5 and 0.5 (seed 0) and biases at 0. The error is the squared difference between output and target. Backpropagation was checked against gradients measured by nudging every weight and bias: the largest difference was about 1e-11, for one and two hidden layers.

## Training method

Stochastic gradient descent (`nn/train.py`): the network learns from one example at a time, updating its weights after each one. Every epoch goes through all 300 examples in a new shuffled order (seeded, so runs repeat exactly), so the network does not learn the frames in one fixed sequence. 2,000 epochs, learning rate 2.0.

## Learning rate

I trained with four rates, keeping everything else the same (same seed, so the same starting weights and shuffle order). Error is the mean squared error on the scaled angles.

| Learning rate | Error after epoch 100 | Error after epoch 2000 |
| --- | --- | --- |
| 0.1 | 0.000263 | 0.0000264 |
| 0.5 | 0.000075 | 0.0000083 |
| 2.0 | 0.000027 | 0.0000039 |
| 30.0 | 0.018233 | 0.014359 |

- 0.1 is too low. It learns, but slowly, and ends about 7 times higher than 2.0.
- 0.5 and 2.0 both fall smoothly. 2.0 is fastest and ends lowest, with an error about 2.1 times lower than 0.5.
- 30.0 is too high. The error jumps around from epoch to epoch and ends at 0.014, about 3,700 times worse than 2.0, so the network does not learn the gait at all. In a shorter test on an earlier gait, 10.0 still learned but its error kept jumping back up.

I chose 2.0. It gave the lowest error and the fastest training with no instability, and trouble only started around 10, so it leaves a wide margin below the point where training breaks.

## Result

With learning rate 2.0 the final error is 0.0000039. Turned back into angles over all 24 joints and 300 frames, the predictions are 0.0010 rad off on average, and 0.017 rad (0.99 degrees) at worst. The worst joint is the L4 tibia. The predicted-against-real graph shows L1's coxa, femur and tibia over one step, where the predictions sit on top of the real angles.

Scored with the GA's fitness, the network's gait gets 2.167 against the GA's 2.227. Everything matches except forward (0.856 against 0.917). Forward only counts a foot as pushing while it is at or below the top of the contact band, so an angle error of under a degree can tip a foot just above that line for a frame and lose that frame's push. It is a small loss, but it shows the fitness is stricter than the error numbers suggest.

## Limits

- The full four-rate comparison uses one seed (0). To check 2.0 against 0.5 was not luck, both were also trained with seeds 1 and 2. 2.0 ended lower every time: 0.0000039, 0.0000037 and 0.0000023 against 0.0000083, 0.0000115 and 0.0000085 for 0.5 (seeds 0, 1 and 2).
- The gait repeats every 60 frames, so all 300 examples are only 60 different moments. To check the network learned the movement rather than memorising those moments, Lauren's held-out test (`nn/held_out_test.py`) trains a fresh network on the even frames only and tests it on the odd frames, which it never sees (the 60-frame repeat keeps every odd frame unseen). The error on the unseen frames (0.0000055) is the same as on the training frames (0.0000055), and the worst unseen angle is 0.023 rad (1.3 degrees) off. Its full 300-frame gait scores 2.167 on the GA's fitness, the same as the network trained on every frame.
- The error was still falling slowly at epoch 2000, so more epochs would lower it a little more.

