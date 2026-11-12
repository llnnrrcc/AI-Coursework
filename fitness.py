"""
fitness.py - scores a gait. Higher is better.

fitness(chromosome) decodes the 36 genes into 300 frames of joint angles (gait.py),
finds where each foot is in each frame (spider_model.py), and adds up the score terms.

Terms (all on a 0 to 1 scale):
  support   - reward frames with at least 4 feet planted (inside the contact band)
  lift      - reward feet that rise clear of the band during the step
  forward   - reward planted feet that sweep backwards, which pushes the body forwards
  below     - penalise feet that go below the band, more the deeper they go
  too_high  - penalise feet that rise far above the body
  crowding  - penalise neighbouring feet that get too close together
Floor numbers come from DECISIONS.md section 2.
"""

import numpy as np

from gait import decode
from spider_model import spider_joints

FLOOR = -0.30
BAND_LOW, BAND_HIGH = -0.35, -0.25   # a foot at or below BAND_HIGH is touching the floor; below BAND_LOW is too deep

# Score every 5th frame only. One step is 60 frames, so that is 12 samples per step.
# One call takes about 0.07 s instead of 0.38 s for all 300 frames, and the GA calls
# this thousands of times.
FRAME_STEP = 5


def feet_positions(angles, frame_step=FRAME_STEP):
    """
    angles: (300, 24) array from decode().
    Returns an array of shape (n_frames, 8, 3): the x, y, z of each foot in each
    sampled frame. Feet are in the spider_joints() order: L1, L2, L3, L4, R4, R3, R2, R1.
    """
    return np.array([[leg[3] for leg in spider_joints(frame)]
                     for frame in angles[::frame_step]])


# The deepest any foot can reach is z = -0.383 (DECISIONS.md section 2), so the deepest
# a foot can be below the band is 0.033. Dividing by this puts the penalty on a 0 to 1
# scale, the same as the reward.
MAX_DEPTH = 0.033

# A foot must rise this far above the top of the contact band to get the full lift
# reward. 0.10 puts the foot about 0.15 above the floor, close to the 0.14 the best
# wave reached in the floor test (DECISIONS.md section 3, Known weakness).
LIFT_TARGET = 0.10

# Four feet on the ground keeps the body supported (two fixed teams of four, section 3).
MIN_PLANTED = 4

# The body is fixed in this model, so forward motion is read from the feet. Front is +x
# (the red marker in the plot). A planted foot that moves towards -x pushes the body
# forwards. DX_TARGET is the backward sweep per sampled frame that the best hand-made
# wave reached (full coxa swing, coxa timing +0.125), so that wave scores about 1.
DX_TARGET = 0.05

# A foot should not go far above the body (body is at z = 0). Nothing in the first
# three terms stopped it: the lift reward is capped at 1, so a foot at z = 1.4 cost
# nothing. The penalty starts just below body level and reaches 1 half a unit above it.
HEIGHT_CAP = -0.05
HEIGHT_SCALE = 0.5

# Neighbouring feet closer than this (seen from above) are penalised. The model has no
# leg thickness, so this is the closest L1 and L2 get in the group's starting gait
# (DECISIONS.md section 3, about 0.5 to 0.56), which the teams are meant to allow. The
# penalty only starts below it, so the planned gait is not punished for what the design
# already accepts.
MIN_FEET_GAP = 0.5
NEIGHBOURS = [(i, (i + 1) % 8) for i in range(8)]   # each foot and the next one round the body

# Weights. Every term runs from 0 to 1.
# Support and below-floor get equal weight. Lift gets half, because with equal weights a
# gait with every foot in the air and nothing planted scores as high as standing (random
# chromosomes averaged 0.90 against standing at 1.00), so the GA could not tell flying
# legs from a working gait. Forward gets full weight: without it standing still scored the
# best possible 1.00 and the GA had no reason to walk. The two penalties added later
# (too high, crowding) have full weight, since they rule out poses that look wrong.
W_SUPPORT = 1.0
W_LIFT = 0.5
W_FORWARD = 1.0
W_BELOW = 1.0
W_TOO_HIGH = 1.0
W_CROWDING = 1.0


def below_floor_penalty(feet):
    """
    How far the feet go below the contact band, averaged over every foot and frame,
    on a scale of 0 (never below) to 1 (always at the deepest point).
    It grows with depth: a foot 0.03 below costs three times a foot 0.01 below.
    """
    z = feet[:, :, 2]
    depth = np.maximum(0.0, BAND_LOW - z)
    return float(np.mean(depth) / MAX_DEPTH)


def support_reward(feet):
    """
    The fraction of sampled frames in which at least 4 feet are planted (z at or below
    the top of the contact band), from 0 to 1. This replaces the plain "feet in the band" term from
    version 1, which also punished lifting a foot, because a lifted foot is out of the band.
    """
    z = feet[:, :, 2]
    planted = z <= BAND_HIGH
    return float(np.mean(planted.sum(axis=1) >= MIN_PLANTED))


def lift_reward(feet):
    """
    How far each foot rises above the top of the contact band at its highest point,
    as a fraction of LIFT_TARGET (capped at 1), averaged over the eight feet.
    A spider that stands still scores 0. A foot that never touches the floor (never at or
    below the top of the band) gets no lift reward, so a leg held up in the air does not count.
    """
    highest = feet[:, :, 2].max(axis=0)
    lowest = feet[:, :, 2].min(axis=0)
    touches = lowest <= BAND_HIGH          # the foot comes down to the floor at some point
    lift = np.clip((highest - BAND_HIGH) / LIFT_TARGET, 0.0, 1.0)
    return float(np.mean(lift * touches))


def forward_reward(feet):
    """
    How far planted feet sweep backwards (towards -x) between sampled frames, averaged
    over every foot and frame and divided by DX_TARGET, capped at 1. A foot counts as
    planted in an interval if it is below the top of the band at both ends. A foot that
    slides forwards while planted pushes the body backwards and cancels the reward.
    Standing still scores 0. Sliding the wrong way scores below 0, down to -1, so the GA
    can tell a slightly wrong gait from a very wrong one.
    """
    z = feet[:, :, 2]
    x = feet[:, :, 0]
    planted = z <= BAND_HIGH
    both = planted[1:] & planted[:-1]
    backward = np.where(both, x[:-1] - x[1:], 0.0)
    return float(np.clip(np.mean(backward) / DX_TARGET, -1.0, 1.0))


def too_high_penalty(feet):
    """
    How far each foot's highest point is above HEIGHT_CAP, as a fraction of HEIGHT_SCALE
    (capped at 1), averaged over the eight feet. A foot at body level costs almost nothing.
    """
    highest = feet[:, :, 2].max(axis=0)
    return float(np.mean(np.clip((highest - HEIGHT_CAP) / HEIGHT_SCALE, 0.0, 1.0)))


def crowding_penalty(feet):
    """
    How far neighbouring feet (seen from above) come within MIN_FEET_GAP of each other,
    as a fraction of MIN_FEET_GAP, averaged over the eight neighbouring pairs and every
    frame. Feet at the same spot would score 1.
    """
    xy = feet[:, :, :2]
    gaps = np.stack([np.linalg.norm(xy[:, a] - xy[:, b], axis=1) for a, b in NEIGHBOURS])
    return float(np.mean(np.maximum(0.0, MIN_FEET_GAP - gaps) / MIN_FEET_GAP))


def fitness(chromosome):
    feet = feet_positions(decode(chromosome))
    return (W_SUPPORT * support_reward(feet)
            + W_LIFT * lift_reward(feet)
            + W_FORWARD * forward_reward(feet)
            - W_BELOW * below_floor_penalty(feet)
            - W_TOO_HIGH * too_high_penalty(feet)
            - W_CROWDING * crowding_penalty(feet))


if __name__ == "__main__":
    import time
    from chromosome import random_chromosome, standing_chromosome

    start = time.time()
    standing = fitness(standing_chromosome())
    one_call = time.time() - start
    rng = np.random.default_rng(0)
    random_scores = [fitness(random_chromosome(rng)) for _ in range(20)]

    print(f"standing: {standing:.3f}")
    print(f"random (20): mean {np.mean(random_scores):.3f}, best {np.max(random_scores):.3f}")
    print(f"one call takes about {one_call:.2f} s")
