# Design decisions

## 1. Joint limits

| Joint | Range (rad) | Applies to | Evidence |
|---|---|---|---|
| Coxa | Different for each leg, e.g. L1 -0.62 to 0.00, L4 +0.14 to +0.47 | Per leg, right side mirrored | `coxa_limits.md`, `coxa_symmetry.md` |
| Femur | -0.5 to -0.2 | Every leg | `femur_limits.md` |
| Tibia | -1.7 to 0.0 | Every leg | `tibia_limits.md` |

The full per-leg table with slot numbers is in `joint_limits_summary.md`.

**Why:** femur and tibia limits come from testing L1 for leg shape, reach and whether the foot can reach the ground, checked against each other because they depend on each other. Coxa limits come from testing the front and back legs against real spider measurements (Wang et al., 2011). They differ per leg because each leg is attached at a different angle around the body, so one shared range would let front legs swing into their neighbours and stop back legs reaching their working range.

**Symmetry rule:** right coxa = minus left coxa. Femur and tibia are the same on both sides.

## 2. Ground height and standing pose

- **Floor:** z = -0.30. A foot counts as planted between -0.35 and -0.25.
- **Standing pose:** femur -0.4 and tibia -1.5 on every leg, with coxa at the middle of each leg's range (L1 -0.31, L2 -0.32, L3 -0.08, L4 +0.31, right side mirrored). All eight feet sit at z = -0.295.

**Why:** the deepest any foot can reach is about -0.383, so a floor at -0.30 lets feet plant across about 60% of the femur range, leaving the rest for lifting legs during a step. Coxa at the middle of each range (rather than 0) gives every leg room to swing both ways, since 0 is at the edge of the front and back legs' ranges.

**Rejected:** a floor at -0.35. Feet could only plant across about a third of the femur range, leaving the GA little room, and its below-floor penalty could never trigger. See `femur_limits.md`.

## 3. Chromosome design

A chromosome is 36 genes: for each of the 12 joints on the left legs, three numbers (offset, amplitude, phase). The right legs copy the left (see "Symmetry and leg teams" below). Each joint angle over the 300 frames is a repeating wave:

`angle(t) = offset + amplitude * sin(2 * pi * 5 * t / 300 + phase)`

In the formula, offset = centre, amplitude = size × (distance from centre to the nearer limit), and phase = 2π × timing. So the ±π/4 coxa window is the same as -0.125 to +0.125 in timing units.

Smooth by design, so there are no sudden jumps between frames. 5 whole cycles in 300 frames means one step takes 60 frames.

**Starting values:** the table below shows the standing pose, which is where each joint's centre starts. The GA can then move each centre anywhere within the joint's limits (see "Keeping genes inside the joint limits" below), so the offsets and maximum amplitudes here only apply at the start.

| Joint | Offset | Max amplitude | Limits |
|---|---|---|---|
| Femur | -0.4 | 0.1 | -0.5 to -0.2 |
| Tibia | -1.5 | 0.2 | -1.7 to 0.0 |
| Coxa L1 | -0.31 | 0.31 | -0.62 to 0.00 |
| Coxa L2 | -0.32 | 0.30 | -0.62 to -0.01 |
| Coxa L3 | -0.08 | 0.46 | -0.54 to +0.38 |
| Coxa L4 | +0.31 | 0.16 | +0.14 to +0.47 |

Right-side coxa: same amplitude, offset sign flipped. Femur and tibia are the same on every leg.

**Why:** the offsets are the standing pose from section 2, and each maximum amplitude is the distance from the offset to the nearest limit, so no wave leaves its joint's range. Whole cycles loop cleanly: the gap between the last and first frame equals one normal frame step (checked on all eight legs). Cycle count changes only speed, so 5 is a judgment call (1 cycle looks like slow motion, 8 looks jittery on the plot).

**Known weakness:** a pure wave cannot hold a foot still on the ground for part of the step. It also pushes the foot through the floor. With the waves centred on the standing pose, which sits on the floor, and the femur and tibia moving in step, L1's foot is below -0.35 for about 32% of each step (amplitudes 0.1 and 0.2). The timing between the femur and tibia matters more than where the waves are centred. Half a step apart, the foot is never below the floor and sits in the contact band for 82% of the step, but it only reaches z = -0.24, about 0.06 above the floor, so the leg would shuffle instead of stepping. Centring higher (femur -0.35, tibia -1.4, amplitudes 0.15 and 0.3) with the timing half a step apart gave 0% below the floor, 28% in the band and a highest foot of -0.16, about 0.14 above the floor. Femur and tibia timing are both genes, so the GA can find the balance between never going below the floor and lifting enough to step. This is not a blocker, and the centres can stay at the standing pose. `fitness.py` should make the below-floor penalty grow with how far below the foot goes, and reward a foot that lifts during the swing, or the GA will learn to shuffle. A duty-cycle gene or a flattened bottom is an option for a second version. The 32% finding and the -0.35 / -1.4 idea came from Claude. The numbers are for L1. I checked them by running them in `explore.py`.

**Symmetry and leg teams:**

- **Right legs copy the left.** Each right leg uses its left partner's genes, half a step later (a phase shift of pi, which is 30 frames at 60 frames per step). The right coxa is also the negative of the left coxa, so the leg mirrors across the body. Femur and tibia copy directly. This halves the chromosome from 72 genes to 36. The cost is that the spider cannot turn, but the brief and the provided video only need straight-line walking.

- **The legs walk in two fixed teams.** Team 1 is L1, L3, R2, R4, and team 2 is L2, L4, R1, R3, as measured on real spiders (Wang et al., 2011). Team 2 moves half a step after team 1, so half the legs are in their stance half of the step at any moment. L1 and L3 have no added timing, L2 and L4 have half a step added, and the right-leg copying above then puts R2 and R4 in team 1 and R1 and R3 in team 2 automatically.

- **Why fixed:** real spiders walk in these teams (Wang et al., 2011), and fixing them means half the legs are always in their stance half of the step, spread across both sides of the body. The GA would otherwise have to discover this pattern by trial and error. Neighbouring legs in opposite teams do pass closest at the turnaround, where L1 and L2's feet come within 0.56 (against 1.59 if they moved in step), but their leg segments stay at least 0.49 apart, so they never cross. `fitness.py` should still penalise neighbouring feet that get too close. To stop the GA undoing the teams, each coxa's timing gene is limited to a small window around its team's timing. Femur and tibia timing stay free, so the GA can still choose when in the step each leg lifts.

**Origin:** the wave design was proposed by Claude. The cycle and floor numbers were run in the model with Claude's help.

### Keeping genes inside the joint limits

Each joint has three genes, each with a fixed range:

| Gene | Range | Meaning |
|---|---|---|
| Centre | The joint's limits (min to max) | The middle of the movement |
| Size | 0 to 1 | How far the joint moves, as a fraction of the room between the centre and the nearer limit |
| Timing | 0 to 1 | Where in the cycle the movement happens |

The joint moves within centre ± size × (distance from centre to the nearer limit), so every chromosome decodes to angles inside the limits. Initialisation draws each gene from its range, and mutation keeps it there (timing wraps round, since 1 is the same point in the cycle as 0).

**Exception for the coxa's timing:** to keep the leg teams fixed (see "Symmetry and leg teams"), the coxa's timing gene runs from -0.125 to +0.125 instead of 0 to 1, and is added to its team's timing: 0 for L1 and L3, 0.5 for L2 and L4. That lets each coxa shift by up to an eighth of a cycle, but never far enough to move the leg into the other team. Mutation keeps it within -0.125 to +0.125 rather than wrapping round. Femur and tibia timing stay at 0 to 1.

### Crossover by leg

Genes are stored leg by leg (L1, L2, L3, L4; the right side mirrors them), 9 genes per leg. Crossover takes each leg whole from one parent or the other. A step only works when a leg's joints are coordinated, for example the femur lifting while the coxa swings forward, so swapping whole legs keeps each working leg intact while still mixing the parents.

### Selection and elitism

**Tournament selection (size 3):** to choose each parent, three chromosomes are picked at random and the one with the highest fitness wins. Fitter chromosomes win more often, so they have more children, but weaker ones still win sometimes when they meet even weaker opponents, which keeps variety in the population. Tournament selection only compares scores, so it works with negative fitness values, which the below-floor penalty can produce.

**Elitism (2):** the two best chromosomes in each generation are copied unchanged into the next one, so the best solution found so far can never be lost to crossover or mutation. In the first test run, the best fitness never dropped from one generation to the next.

**Starting settings:** population 40, 50 generations, mutation rate 0.1, tournament size 3, elitism 2. With fitness taking about 0.06 seconds per call, a run takes about 2 minutes. All settings are constants at the top of `ga.py`, so experiments only change one number. Each run uses a seeded random generator, so the same seed gives the same starting population.

## 4. Rejected options

### Every angle for every frame (7,200 genes)

One gene per joint per frame (300 × 24). Rejected because:

- **Crossover would break the walk:** a cut at any frame joins two gaits that are almost certainly in different poses at that moment, so the child would jump between them in a single frame.
- **Mutation would cause twitches:** each gene controls one joint in one frame, so a mutation changes that frame alone and the leg flicks out of place and back.
- **The search space would be too large:** 7,200 genes against 36 for the wave design (section 3). A walk is smooth and repeating, but this encoding would have to discover both frame by frame instead of having them built in.

Adding a smoothness penalty to the fitness would not fix this, because crossover and mutation would keep creating jumps and twitches every generation.


### Independent genes for every leg (72 genes)

Each of the 24 joints has its own offset, amplitude and phase. Rejected because:

- **It doubles the search space for no benefit:** straight-line walking needs left and right to mirror anyway, so the GA would spend its time rediscovering symmetry that can be built in.
- **The extra freedom only buys turning,** which the brief and the provided video do not require.
- **If turning is needed later,** one extra gene that lengthens one side's steps would allow gentle turns, without going back to 72.

### Letting the GA find the leg teams

Every phase gene free, with the fitness function rewarding four feet on the ground. Rejected because:

- **The GA would have to discover the team pattern by trial and error,** which may not happen in the time available.
- **Until it does, the legs have no consistent pattern,** so the spider may not keep half its legs in stance at any moment.
- **Real spiders use these teams** (Wang et al., 2011), so building them in costs no realism.

### Clipping angles to the limits afterwards

Genes could take any value, with angles clipped to the joint limits when decoding. Rejected because:

- **Movement would stall at the limits:** any part of a wave beyond a limit becomes a flat stretch, so the joint stops abruptly and holds still.
- **The search would waste effort:** many different chromosomes would decode to the same clipped movement, so the fitness could not tell them apart and the GA would have no direction to improve in.

### Unrestricted crossover

Crossover could cut anywhere in the gene list. Rejected because:

- **It could split a joint:** a joint's centre could come from one parent and its size from the other. Size is measured from the centre, so the movement would change unpredictably.
- **It could split a leg:** the femur's timing could come from one parent and the coxa's from the other, so the lift would no longer line up with the forward swing and the foot would drag.


### Roulette wheel selection

Each chromosome's chance of being picked is proportional to its fitness. Rejected because:

- **It cannot handle negative scores:** the below-floor penalty can make fitness negative, and a negative share of the wheel has no meaning.
- **One strong chromosome can take over:** if one score is much higher than the rest, it is picked almost every time, and the population loses variety quickly.