# Neural network training (Part 2)

## What the network learns

The network learns to reproduce the GA's final walking gait (`final_best_chromosome.npy`: population 80, seed 1, 100 generations, fitness 2.354 with the energy term). An earlier version of this write-up used the GA's previous final gait, from before the energy term; all numbers below are for the current one. Given where the spider is in its step, it outputs all 24 joint angles for that moment.

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
| 0.1 | 0.000214 | 0.000019 |
| 0.5 | 0.000088 | 0.0000031 |
| 2.0 | 0.000014 | 0.0000011 |
| 30.0 | 0.010492 | 0.012436 |

- 0.1 is too low. It learns, but slowly: after the first drop it sits on a shelf between 0.0002 and 0.0001 until about epoch 500.
- 0.5 and 2.0 both fall smoothly. 2.0 is fastest (below 0.00001 by about epoch 150) and ends lowest, with an error about 2.8 times lower than 0.5.
- 30.0 is too high. The error jumps around from epoch to epoch and stays around 0.01, so the network does not learn the gait at all. In a shorter test on the earlier gait, 10.0 still learned but its error kept jumping back up.

I chose 2.0. It gave the lowest error and the fastest training with no instability, and trouble only started around 10, so it leaves a wide margin below the point where training breaks.

## Result

With learning rate 2.0 the final error is 0.0000011. Turned back into angles over all 24 joints and 300 frames, the predictions are 0.0006 rad off on average, and 0.0085 rad (0.48 degrees) at worst. The worst joint is the R3 tibia. The predicted-against-real graph shows L1's coxa, femur and tibia over one step, where the predictions sit on top of the real angles. In this gait L1's coxa barely moves (0.024 rad in total), so the graph mainly shows the femur and tibia.

## Limits

- The full four-rate comparison uses one seed (0). To check 2.0 against 0.5 was not luck, both were also trained with seeds 1 and 2. 2.0 ended lower every time: 0.0000011, 0.0000012 and 0.0000010 against 0.0000031, 0.0000050 and 0.0000043 for 0.5 (seeds 0, 1 and 2).
- The gait repeats every 60 frames, so all 300 examples are only 60 different moments. To check the network learned the movement rather than memorising those moments, Lauren's held-out test (`nn/held_out_test.py`) trains a fresh network on the even frames only and tests it on the odd frames, which it never sees (the 60-frame repeat keeps every odd frame unseen). The error on the unseen frames (0.0000015) is the same as on the training frames (0.0000015), and the worst unseen angle is 0.011 rad (0.61 degrees) off. Its full 300-frame gait scores 2.354 on the GA's fitness, the same as the GA's own final gait.
- The error was still falling slowly at epoch 2000, so more epochs would lower it a little more.

