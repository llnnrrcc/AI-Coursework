# Reflection on the neural network (Part 2)

Draft for the group to check. For each weakness I've said what the evidence is and what I think would improve it. None of the improvements have been tested.

## What went well

The network learned the movement rather than memorising the frames. Lauren's held-out test trains a fresh network on the even frames only and tests it on the odd frames, which it never sees. The error came out the same on both (0.0000055), and the worst unseen angle was 1.3 degrees off.

It walks almost exactly like the GA. When I scored the network's 300-frame gait with the GA's fitness it got 2.167 against the GA's 2.227, and its angles are 0.0010 rad off on average. Support and lift match exactly and the penalties to within 0.003; the gap is almost all in forward, which I come back to below.

We know backpropagation is right, not just that the error goes down. The gradient check in `nn/network.py` compares it with gradients measured by nudging every weight, and they match to about 1e-11 for one and two hidden layers.

The main choices come from experiments rather than guesses. I compared four learning rates and then checked 2.0 against 0.5 on three seeds, and 2.0 won every time. The architecture comparison tried six network sizes.

We found the problems in the fitness by watching what the evolved gaits actually did, not just by reading their scores. Four loopholes came up this way: feet sinking under the floor, legs held up in the air, the forward reward stopping at 0, and lazy back legs (`fitness_design.md`).

The lazy back legs are the clearest example. The previous final gait scored perfectly, but in `show_best.py` its front and back legs barely moved. The numbers backed that up: forward was averaged over all eight feet before it was capped, so L3 and R3 were pushing 2.8 and 3.0 times their share while the back legs pushed only 0.02 of theirs. Lauren changed forward so each foot is capped on its own. In the new final gait every coxa swings between 0.30 and 0.50 rad and the back legs push 0.69 of their share instead of 0.02. A perfect score had hidden a gait that only looked wrong once someone watched it.

## Weaknesses

### Joints at their limits are learned less well

The output layer is a sigmoid, which only gets close to 0 and 1 and never reaches them, and it goes very flat near both ends. So the network struggles with any joint whose target sits at one of its limits. In the final gait the back legs' tibias (L4 and R4) bend all the way to the -1.7 rad limit, which is a target of exactly 0, and those are the two worst joints: 0.99 degrees off at worst (L4 tibia, frame 93), when no other joint is worse than 0.37 degrees. Across all joints, targets within 0.03 of either end average 0.0018 rad of error, twice the 0.0009 rad everywhere else.

Scaling the targets to 0.05 to 0.95 instead of 0 to 1 should fix this, because no target would sit in the flat part of the sigmoid, and the predicted angles would still stay inside the joint limits.

### Small angle errors cost forward score

The network's gait loses 0.06 of forward (0.856 against the GA's 0.917) even though its angles are under a degree off. Forward only counts a foot as pushing while it is at or below the top of the contact band, so a tiny error can lift a foot just over that line for a frame and that frame's push is lost. The error numbers make the network look closer to the GA than the fitness does.

Training could weight the frames where a foot is near that line more heavily, or the fitness could use a softer edge than a hard cut-off at the top of the band.

### The network can only do one walk

It was trained on one gait, so that's the only gait it can produce. It can't walk faster or slower, and it can't turn. Its only inputs are the sine and cosine of the step phase, so nothing tells it how fast to go or which way, and for a given moment in the step it always gives the same answer.

To fix this I'd run the GA a few times for different speeds (for example by changing the forward target), train on all of those gaits together, and add the speed as a third input.

### The fitness caps decide the walk

The GA has no reason to push past the forward target, so it doesn't. In the final gait the front and middle legs each sweep 0.98 to 1.03 of the target, right at the cap (`fitness_design.md`). So the walking speed comes from a number we picked, not from what a real spider does, and the network inherits that because it learns this gait. The back legs also still push less than the others (0.69 of the target), so the per-leg fix helped but didn't finish the job.

A speed reward that keeps rising instead of a capped forward term, or caps based on real spider data, would let the walk be decided by something more meaningful.

### One seed for most comparisons

The architecture comparison and the full four-rate learning-rate comparison each used one seed, so one unlucky start could change a close result. The one comparison I did check on more seeds held up: learning rate 2.0 beat 0.5 on seeds 0, 1 and 2 (0.0000039, 0.0000037 and 0.0000023 against 0.0000083, 0.0000115 and 0.0000085). The architecture results haven't been checked like that. On the current gait [2, 32, 24] and [2, 16, 16, 24] end 1.5 to 1.8 times lower than [2, 16, 24] (0.0000026 and 0.0000022 against 0.0000039), which is a small enough gap that another seed could change it.

The fix is to repeat the architecture comparison with three seeds and report the average and spread, the same way I did for the GA settings in `experiments.md`.

### No physics or inverse kinematics

The model has no gravity, balance or friction, and the body is fixed in place. Forward motion is worked out from feet sweeping backwards while they touch the floor, not from the body actually moving, and the fitness only looks at where the feet are. The joint angles are generated directly too, so no foot is ever placed at a point we chose, which means there's no inverse kinematics. The brief says full physics isn't needed, but this is still the biggest gap between our model and a real spider.

The next step would be running the final gait in the provided Webots model, which does have physics, to see whether the spider actually moves forward and stays upright. Inverse kinematics could then plan where each foot goes, with the network learning the angles that get it there.

## How this was made

Drafted with Claude's help for structure legibility and flow. The figures for joints at their limits and the network's fitness breakdown were measured on the network trained on the final gait, for this reflection.
