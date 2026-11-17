# Reflection on the neural network (Part 2)

Draft for the group to check. For each weakness I've said what the evidence is and what I think would improve it. None of the improvements have been tested.

## What went well

The network learned the movement rather than memorising the frames. Lauren's held-out test trains a fresh network on the even frames only and tests it on the odd frames, which it never sees. The error came out the same on both (0.0000015), and the worst unseen angle was 0.61 degrees off.

It also reproduces the GA's walk. When I scored the network's 300-frame gait with the GA's fitness it got 2.354, exactly the same as the GA's own final gait, and its angles are 0.0006 rad off on average.

We know backpropagation is right, not just that the error goes down. The gradient check in `nn/network.py` compares it with gradients measured by nudging every weight, and they match to about 1e-11 for one and two hidden layers.

The main choices come from experiments rather than guesses. I compared four learning rates and then checked 2.0 against 0.5 on three seeds, and 2.0 won every time. The architecture comparison tried six network sizes, and [2, 16, 24] was the smallest that reached the best error.

On the GA side, we found three loopholes in the fitness by looking at what the evolved gaits were actually doing, not just at their scores: feet sinking under the floor, legs held up in the air, and the forward reward stopping at 0. Each one was fixed (`fitness_design.md`).

## Weaknesses

### Joints near their limits are learned less well

The output layer is a sigmoid, which only gets close to 0 and 1 and goes very flat near them, so the network learns more slowly when a joint's target is near one of its limits. I measured this on the saved model. The targets run from 0.008 to 0.992 of each joint's range, and for targets within 0.03 of either end the average error is 0.0011 rad, twice the 0.00055 rad everywhere else. The single worst error (0.48 degrees, the R3 tibia at frame 270) is at a target of 0.033, and the next two worst joints, the L3 and R3 coxas, are the ones whose targets reach 0.008 and 0.992.

I think scaling the targets to 0.05 to 0.95 instead of 0 to 1 would fix this, because no target would sit in the flat part of the sigmoid, and the predicted angles would still stay inside the joint limits.

### The network can only do one walk

It was trained on one gait, so that's the only gait it can produce. It can't walk faster or slower, and it can't turn. Its only inputs are the sine and cosine of the step phase, so nothing tells it how fast to go or which way, and for a given moment in the step it always gives the same answer.

To fix this I'd run the GA a few times for different speeds (for example by changing the forward target), train on all of those gaits together, and add the speed as a third input.

### The fitness caps decide the walk

Once we added the energy term, the GA settled on the least movement that still maxes out the forward and lift rewards. Every foot lifts 0.10 to 0.11 above the contact band, right at the 0.10 lift target, and the forward reward sits exactly at its cap (`fitness_design.md`). So the walk is shaped by the numbers we picked for those caps, not by what a real spider does, and the network inherits that because it learns this gait.

A speed reward that keeps rising instead of a capped forward term, or caps based on real spider data, would let the walk be decided by something more meaningful.

### Stiff front and back legs

This was a side effect nobody planned. In the final gait L1's coxa swings only 0.024 rad in total and L4's only 0.006 rad, while L2 and L3 swing theirs 0.35 and 0.89 rad. The energy term moved the sideways swinging onto the middle legs, and the front and back legs push with the femur and tibia instead. It still scores perfectly on support, lift and forward.

[Group: add what we decided about this, for example that we accepted it as a side effect of the energy term.]

A lower energy weight, or measuring energy per leg so no single leg can stop moving to save cost, should spread the movement out again.

### One seed for most comparisons

The architecture comparison and the full four-rate learning-rate comparison each used one seed, so one unlucky start could change a close result. The one comparison I did check on more seeds held up: learning rate 2.0 beat 0.5 on seeds 0, 1 and 2 (0.0000011, 0.0000012 and 0.0000010 against 0.0000031, 0.0000050 and 0.0000043). The architecture results haven't been checked like that, and [2, 16, 24], [2, 32, 24] and [2, 16, 16, 24] finish within about 20% of each other, which is close enough that another seed could reorder them.

The fix is to repeat the architecture comparison with three seeds and report the average and spread, the same way I did for the GA settings in `experiments.md`.

### No physics or inverse kinematics

The model has no gravity, balance or friction, and the body is fixed in place. Forward motion is worked out from feet sweeping backwards while they touch the floor, not from the body actually moving, and the fitness only looks at where the feet are. The joint angles are generated directly too, so no foot is ever placed at a point we chose, which means there's no inverse kinematics. The brief says full physics isn't needed, but this is still the biggest gap between our model and a real spider.

The next step would be running the final gait in the provided Webots model, which does have physics, to see whether the spider actually moves forward and stays upright. Inverse kinematics could then plan where each foot goes, with the network learning the angles that get it there.

## How this was made

Drafted with Claude's help for structure legibility and flow. The figures for joints near their limits were measured on the saved model (`nn/model.npz`) for this reflection.
