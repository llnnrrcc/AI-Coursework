# Network architecture (Part 2)

The final network is [2, 16, 24]: 2 inputs (sine and cosine of the step phase), one hidden layer of 16 neurons, and 24 outputs (one per joint angle). The inputs and outputs are fixed by the problem (see `training.md`), so only the hidden layers were chosen.

## What was tested

Six network sizes, trained on the same data (the GA's final gait) with the same learning rate (2.0), epochs (2,000) and seed, so only the layers differ. Run with `python -m nn.architectures`; the loss curves are in `architectures.png`.

| Layers | Weights and biases | Final error | Time (s) | Gait score |
| --- | --- | --- | --- | --- |
| [2, 2, 24] | 78 | 0.00028 | 14.7 | 2.119 |
| [2, 4, 24] | 132 | 0.000085 | 14.9 | 2.147 |
| [2, 8, 24] | 240 | 0.000012 | 15.0 | 2.193 |
| [2, 16, 24] | 456 | 0.0000039 | 15.3 | 2.167 |
| [2, 32, 24] | 888 | 0.0000026 | 16.0 | 2.224 |
| [2, 16, 16, 24] | 728 | 0.0000022 | 21.7 | 2.194 |

The gait score is the network's output scored with the GA's own fitness function. The GA's gait scores 2.227.

## Too small (2 and 4 hidden neurons)

The networks with 2 and 4 hidden neurons stop improving early because there aren't enough of them to cover all the work needed: they have to reproduce 24 different joint movements at once. On the loss graph, the 2-neuron line goes flat within about 20 epochs and the 4-neuron line by about 250. Training them for longer would not help, because they are already doing their best with the neurons they have. More training only improves the neurons that exist; it can't add more.

## Why the gait score jumps around

The gait score is not a fair way to compare network sizes because it partly depends on luck. The fitness counts a foot as touching the floor if it is at or below a line (z = -0.25), and the GA's gait only lifts its feet just above that line. The network's feet are off by tiny amounts (less than 0.005), and sometimes that pushes a foot onto the wrong side of the line. The fitness then thinks the foot is touching the floor while it moves forwards, which takes points off. This is why the 8-neuron network scored higher than the 16-neuron one in a single run. The same 16-neuron network scored anywhere from 2.167 to 2.226 depending only on its random starting weights.

## Choice: 16 hidden neurons

Because the gait score partly depends on luck, we measured how far each network's feet end up from the GA's feet instead. We trained 8, 16 and 32 hidden neurons three times each, with different random starting weights (`python -m nn.size_check`).

| Hidden neurons | Worst foot error (3 runs) | Average gait score |
| --- | --- | --- |
| 8 | 0.0062 | 2.182 |
| 16 | 0.0047 | 2.196 |
| 32 | 0.0043 | 2.184 |

We chose 16 hidden neurons because it is the smallest network whose feet were within 0.005 of the GA's every time; 8 went over twice. We did not choose 32 because it was not better overall: its average gait score was lower than 16's, and it has twice as many weights (888 against 456).

## Two hidden layers

We also tried two hidden layers of 16 neurons. We did not use them because it took about 40% longer to train (21.7 s against 15.3 s) and the gait score was no better (2.194, against 2.196 on average for one layer of 16). We didn't need a second layer: the only input is where the spider is in its step, so the problem is simple enough for one layer.

## Limits

- Every network was trained for 2,000 epochs. The 16, 32 and two-layer networks were still slowly improving at that point, so the comparison is at a fixed training time.
- The size check used 3 random starts per size. More would give a firmer answer.
- The held-out test (train on even frames, test on odd frames) shows the network fills in moments between frames correctly, but every moment is still within one repeated step.

## How this was made

Claude wrote `architectures.py` and `size_check.py` and helped me structure this write-up; I ran the experiments, chose the network size, and wrote the reasoning in each section.