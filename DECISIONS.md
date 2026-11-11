# Design decisions

Draft: joint limits and ground height awaiting group sign-off. Chromosome design drafted in section 3, awaiting sign-off.

Each decision links to the file holding the full evidence.

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

Smooth by design, so there are no sudden jumps between frames. 5 whole cycles in 300 frames means one step takes 60 frames.

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

**Known weakness:** a pure wave cannot hold a foot still on the ground for part of the step. Worse, the standing pose sits on the floor, so a wave centred on it puts about 32% of frames below -0.35 (foot z runs from -0.378 to -0.125 over a cycle) and the below-floor penalty fires constantly. Open for the group: centre the offsets above the standing pose (for example femur -0.35, tibia -1.4, not yet tested), or add a duty-cycle gene or a flattened bottom in a second version.

**Symmetry and leg teams:**

- **Right legs copy the left.** Each right leg uses its left partner's genes, half a step later (a phase shift of pi, which is 30 frames at 60 frames per step). The right coxa is also the negative of the left coxa, so the leg mirrors across the body. Femur and tibia copy directly. This halves the chromosome from 72 genes to 36. The cost is that the spider cannot turn, but the brief and the provided video only need straight-line walking.

- **The legs walk in two fixed teams.** Team 1 is L1, L3, R2, R4, and team 2 is L2, L4, R1, R3, as measured on real spiders (Wang et al., 2011). Team 2 moves half a step after team 1, so four feet are always on the ground. L1 and L3 have no added timing, L2 and L4 have half a step added, and the right-leg copying above then puts R2 and R4 in team 1 and R1 and R3 in team 2 automatically.

- **Why fixed:** neighbouring legs are always in opposite teams, so they never swing through the same space at the same time. This removes the overlap found on Day 3, where L1 and L2's feet came within 0.56 of each other (`joint_limits_summary.md`, open point 2). To stop the GA undoing the teams, each coxa's phase gene is limited to a small window (plus or minus pi/4) around its team's timing. Femur and tibia phases stay free, so the GA can still choose when in the step each leg lifts.

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
- **Until it does, neighbouring legs can swing into each other,** since their coxa ranges overlap (L1 and L2's feet came within 0.56).
- **Real spiders use these teams** (Wang et al., 2011), so building them in costs no realism.

### Clipping angles to the limits afterwards

Genes could take any value, with angles clipped to the joint limits when decoding. Rejected because:

- **Movement would stall at the limits:** any part of a wave beyond a limit becomes a flat stretch, so the joint stops abruptly and holds still.
- **The search would waste effort:** many different chromosomes would decode to the same clipped movement, so the fitness could not tell them apart and the GA would have no direction to improve in.

### Unrestricted crossover

Crossover could cut anywhere in the gene list. Rejected because:

- **It could split a joint:** a joint's centre could come from one parent and its size from the other. Size is measured from the centre, so the movement would change unpredictably.
- **It could split a leg:** the femur's timing could come from one parent and the coxa's from the other, so the lift would no longer line up with the forward swing and the foot would drag.