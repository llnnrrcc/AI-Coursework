# Reflection on the neural network (Part 2)

Each weakness below comes with the evidence for it and a suggested improvement. None of the improvements have been tested.

## What went well

The network learned the movement, not a list of frames. The held-out test trains a fresh network on the even frames only and tests it on the odd frames, which it never sees. The error was the same on both (0.0000055), and the worst unseen angle was only 1.3 degrees off.

It also walks almost exactly like the GA. Scored with the GA's own fitness function, the network's gait gets 2.167 against the GA's 2.227, with angles 0.0010 rad off on average. Support and lift match exactly and the penalties are within 0.003, so nearly the whole gap is in forward, which is covered under the weaknesses.

Backpropagation was proven correct, not just assumed from a falling error. The gradient check matches it against measured gradients to about 1e-11, for one and two hidden layers. The PyTorch comparison (`pytorch_comparison.md`) then trained the same network with matched settings and ended with weights within 1.95e-13 of ours, the same error and the same gait score (2.166839).

The main settings came from experiments. Four learning rates were compared, and 2.0 then beat 0.5 on all three seeds tried. The network size was checked over three random starts: 16 hidden neurons kept the worst foot error under 0.005 every time, while 8 did not, and 32 gave no better gait score for twice the weights.

The fitness problems were found by watching the gaits, not by reading the scores. Four loopholes came up this way: feet sinking under the floor, legs held in the air, the forward reward stopping at 0, and lazy back legs. The lazy back legs are the clearest case. The previous final gait scored perfectly, but in show_best.py its front and back legs barely moved. The numbers backed that up: L3 and R3 were pushing 2.8 and 3.0 times their share of the forward target while the back legs pushed 0.02 of theirs. After the per-leg fix, the back legs push 0.69 of their share and every coxa swings between 0.30 and 0.50 rad. A perfect score had hidden a gait that only looked wrong once someone watched it.

## Weaknesses

### Joints at their limits are learned less well

The output layer uses a sigmoid, which gets close to 0 and 1 but never reaches them, and flattens out near both. In the final gait the back legs' tibias bend right to the -1.7 rad limit, which is a target of exactly 0. Those two joints have the worst errors by a distance: 0.99 degrees for the L4 tibia (frame 93) and 0.97 for R4, when no other joint is worse than 0.37. Across all joints, targets within 0.03 of either end average 0.0018 rad of error, twice the 0.0009 rad elsewhere.

Scaling the targets to 0.05 to 0.95 instead of 0 to 1 should fix this. No target would sit in the flat part of the sigmoid, and every predicted angle would still stay inside its joint limits.

### Small angle errors cost forward score

The network's gait loses 0.06 of forward (0.856 against the GA's 0.917), even though its angles are under a degree off. Forward only counts a foot as pushing while it sits at or below z = -0.25, so a tiny error can lift a foot just over that line for a frame, and that frame's push is lost.

The PyTorch comparison shows the same thing from the other side. PyTorch's default settings ended with a higher training error (0.0000145) but a higher gait score (2.2249). Training error and gait quality measure different things, and lowering one doesn't guarantee the other.

Training could weight the frames where a foot is near the -0.25 line more heavily. Alternatively, the fitness could use a softer edge than a hard cut-off.

### The network can only do one walk

The network was trained on one gait, so that is the only gait it can produce. It can't walk faster, slower or turn. Its only inputs are the sine and cosine of the step phase, and the gait repeats every 60 frames, so the whole training set is 60 different moments of one step.

A fix would be to run the GA several times for different speeds, train on all of those gaits together, and add speed as a third input.

### The fitness caps decide the walk

The GA has no reason to push past the forward target, so it doesn't. In the final gait the front and middle legs each push 0.98 to 1.03 of the target, right at the cap, so the walking speed comes from a number we picked rather than from what a real spider does. The network learns this gait, so it inherits the same limit. The back legs also still push less than the others (0.69 of the target), so the per-leg fix helped without fully solving it.

A speed reward that keeps rising instead of a capped forward term would let the walk be decided by something more meaningful than the cap.

### Only three seeds for the comparisons

Three seeds is enough to catch a lucky run but not to settle a close result. The full four-rate learning-rate comparison used one seed, and only 2.0 against 0.5 was repeated on three: 2.0 won each time (0.0000039, 0.0000037 and 0.0000023, against 0.0000083, 0.0000115 and 0.0000085). In the size check, the worst foot errors for 8, 16 and 32 neurons were 0.0062, 0.0047 and 0.0043, and the average gait scores were within 0.014 of each other. Gaps that small could shift with more runs.

Ten seeds per setting, with the average and spread reported, would firm these up.

### No physics or inverse kinematics

The model has no gravity, balance or friction, and the body is fixed in place. Forward motion is worked out from feet sweeping backwards while they touch the floor, not from the body actually moving.

To see how much that matters, we played the GA's final gait (2.227) on the module's physics spider in Webots for 30 seconds. It needed three changes to walk properly. The robot's hip motors couldn't swing the legs at their 50 N m limit (they moved 0.001 rad at full torque), so we raised them to 100 N m. The Webots legs stand in two straight rows, while ours fan out round the body, so with every hip at 0 the back legs caught on each other and tangled; standing each Webots hip at its leg's angle in our model fixed that. Fanning the legs on the robot's tilted hips also lowered the front and back feet, leaving the third pair hovering, so each thigh was raised to level the feet again.

With all three changes and self-collision on, the spider walked 8.72 m forwards in 30 seconds and drifted 0.79 m to the side. Without the levelling it managed 4.05 m, with the legs straight out 0.47 m, and with the module's original hip motors the same thigh and knee movements pushed it 1.52 m backwards. So the forward motion really does come from the hip swing that our forward term rewards, and the gait walks far better when the legs are spaced and levelled like ours. One front foot still drags while it swings, and lifting it clear cut the distance to 4.04 m, so this gait relies on it. The distance can't be compared with the fitness score, and only the GA's gait was run, not the network's. The full results are in webots/README.md.

Scoring each gait by how far it walks in Webots, with self-collision on, would make the GA optimise the actual walk rather than a stand-in for it. Each run took about 30 seconds of simulation, against a fraction of a second for the kinematic fitness, so this would suit a final tuning stage rather than the whole GA run.
