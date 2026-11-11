"""
fitness.py - scores a gait. Higher is better.

fitness(chromosome) decodes the 36 genes into 300 frames of joint angles (gait.py),
finds where each foot is in each frame (spider_model.py), and adds up the score terms.

Terms (all on a 0 to 1 scale):
  support  - reward frames with at least 4 feet planted (inside the contact band)
  lift     - reward feet that rise clear of the band during the step
  below    - penalise feet that go below the band, more the deeper they go
Floor numbers come from DECISIONS.md section 2.
"""

import numpy as np

from gait import decode
from spider_model import spider_joints

FLOOR = -0.30
BAND_LOW, BAND_HIGH = -0.35, -0.25   # a foot counts as planted inside this band

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

# All three terms run from 0 to 1. Support and below-floor get equal weight. Lift gets
# half, because with equal weights a gait with every foot in the air and nothing planted
# scores as high as standing (random chromosomes averaged 0.90 against standing at 1.00),
# so the GA could not tell flying legs from a working gait. At half weight random gaits
# average 0.45 while sensible stepping gaits score 1.05 to 1.25, above standing at 1.00.
W_SUPPORT = 1.0
W_LIFT = 0.5
W_BELOW = 1.0


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
    The fraction of sampled frames in which at least 4 feet are planted (z inside the
    contact band), from 0 to 1. This replaces the plain "feet in the band" term from
    version 1, which also punished lifting a foot, because a lifted foot is out of the band.
    """
    z = feet[:, :, 2]
    planted = (z >= BAND_LOW) & (z <= BAND_HIGH)
    return float(np.mean(planted.sum(axis=1) >= MIN_PLANTED))


def lift_reward(feet):
    """
    How far each foot rises above the top of the contact band at its highest point,
    as a fraction of LIFT_TARGET (capped at 1), averaged over the eight feet.
    A spider that stands still scores 0.
    """
    highest = feet[:, :, 2].max(axis=0)
    return float(np.mean(np.clip((highest - BAND_HIGH) / LIFT_TARGET, 0.0, 1.0)))


def fitness(chromosome):
    feet = feet_positions(decode(chromosome))
    return (W_SUPPORT * support_reward(feet)
            + W_LIFT * lift_reward(feet)
            - W_BELOW * below_floor_penalty(feet))


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
