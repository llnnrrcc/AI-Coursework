"""
gait.py - turns a 36-gene chromosome into a walk: 300 frames of 24 joint angles.

Each joint moves as a repeating wave (DECISIONS.md, section 3):

    angle(t) = offset + amplitude * sin(2 * pi * N_CYCLES * t / N_FRAMES + phase)

The genes are turned into the wave's numbers like this:
    offset    = centre
    amplitude = size * (distance from the centre to the nearer limit)
    phase     = 2 * pi * (timing + the leg's team timing)

Because the amplitude never reaches past the nearer limit, the wave always stays
inside the joint's limits, so nothing has to be clipped afterwards.

Leg teams: L1 and L3 have no added timing, L2 and L4 have half a cycle added.
The team timing is added to all three joints of a leg, so each timing gene means
"when, within this leg's own step". A leg's femur and tibia timing therefore keep the
same meaning whichever team the leg is in.

Right legs copy their left partner half a cycle later, with the coxa negated so the
leg mirrors across the body. Together with the team timing this puts L1, L3, R2, R4
in one team and L2, L4, R1, R3 in the other.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from chromosome import (N_GENES, N_LEGS, JOINTS_PER_LEG, CENTRE, SIZE, TIMING,
                        gene_index, joint_limits)
from spider_model import draw_legs

N_FRAMES = 300
N_CYCLES = 5                      # 5 steps in 300 frames, so one step is 60 frames
TEAM_TIMING = [0.0, 0.5, 0.0, 0.5]  # extra timing (in cycles) for L1, L2, L3, L4

# In the 24-angle vector the legs are ordered L1, L2, L3, L4, R4, R3, R2, R1,
# so the right partner of left leg k sits at position 7 - k.
RIGHT_PARTNER = [7, 6, 5, 4]


def joint_wave(centre, size, timing, limits, extra_timing=0.0):
    """One joint's angle for every frame, as an array of N_FRAMES numbers."""
    low, high = limits
    offset = centre
    amplitude = size * min(centre - low, high - centre)   # never reaches past a limit
    phase = 2 * np.pi * (timing + extra_timing)
    t = np.arange(N_FRAMES)
    return offset + amplitude * np.sin(2 * np.pi * N_CYCLES * t / N_FRAMES + phase)


def decode(chromosome):
    """
    chromosome: NumPy array of 36 genes (see chromosome.py)
    Returns a (300, 24) array: row t holds the 24 joint angles for frame t,
    in the same order that spider_joints() and plot_spider_pose() expect.
    """
    chromosome = np.asarray(chromosome, dtype=float)
    if chromosome.shape != (N_GENES,):
        raise ValueError(f"expected {N_GENES} genes, got shape {chromosome.shape}")

    angles = np.zeros((N_FRAMES, 24))
    for leg in range(N_LEGS):
        right = RIGHT_PARTNER[leg]
        for joint in range(JOINTS_PER_LEG):
            centre = chromosome[gene_index(leg, joint, CENTRE)]
            size = chromosome[gene_index(leg, joint, SIZE)]
            timing = chromosome[gene_index(leg, joint, TIMING)]
            limits = joint_limits(leg, joint)
            team = TEAM_TIMING[leg]

            # Left leg: the wave with its team's timing added
            angles[:, leg * 3 + joint] = joint_wave(centre, size, timing, limits, team)

            # Right partner: the same wave half a cycle later
            right_wave = joint_wave(centre, size, timing, limits, team + 0.5)
            if joint == 0:
                right_wave = -right_wave      # mirror the coxa across the body
            angles[:, right * 3 + joint] = right_wave
    return angles


def animate(angles, interval=33, save_as=None):
    """
    Play the frames as an animation (interval = milliseconds per frame, 33 is about 30 fps).
    save_as: optional file name ending in .gif to save instead of showing a window.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    t = np.linspace(0, 2 * np.pi, 100)

    def draw(frame):
        ax.cla()
        ax.plot(1.5 * np.cos(t), np.sin(t), np.zeros_like(t), color="black", linewidth=3)
        ax.scatter(1.7, 0, 0, color="red", marker="^", s=80)   # front of the spider
        draw_legs(ax, angles[frame])
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4); ax.set_zlim(-2, 2)
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
        ax.set_title(f"Frame {frame + 1} of {len(angles)}")

    anim = FuncAnimation(fig, draw, frames=len(angles), interval=interval)
    if save_as:
        anim.save(save_as, writer="pillow", fps=1000 // interval)
    else:
        plt.show()
    return anim


def check_decode(n_tests=100, seed=0):
    """The 'done when' checks: limits, right legs mirror the left, and the walk loops."""
    from chromosome import random_chromosome, standing_chromosome
    from spider_model import spider_joints

    rng = np.random.default_rng(seed)
    half = N_FRAMES // (2 * N_CYCLES)       # half a cycle = 30 frames
    tolerance = 1e-9                        # allow for rounding in the last decimal place

    for _ in range(n_tests):
        angles = decode(random_chromosome(rng))
        assert angles.shape == (N_FRAMES, 24)

        for leg in range(N_LEGS):
            right = RIGHT_PARTNER[leg]
            for joint in range(JOINTS_PER_LEG):
                low, high = joint_limits(leg, joint)
                left_angles = angles[:, leg * 3 + joint]
                right_angles = angles[:, right * 3 + joint]
                # 1. Left leg inside its limits
                assert left_angles.min() >= low - tolerance and left_angles.max() <= high + tolerance
                # 2. Right leg inside the mirrored limits (coxa flipped, femur/tibia the same)
                r_low, r_high = (-high, -low) if joint == 0 else (low, high)
                assert right_angles.min() >= r_low - tolerance and right_angles.max() <= r_high + tolerance
                # 3. Right leg copies the left half a cycle later (coxa negated)
                sign = -1 if joint == 0 else 1
                assert np.allclose(right_angles, sign * np.roll(left_angles, -half))

    # 4. The standing chromosome stands still with all eight feet on the floor
    standing = decode(standing_chromosome())
    assert np.allclose(standing, standing[0])
    feet_z = [leg[3][2] for leg in spider_joints(standing[0])]
    assert np.allclose(feet_z, -0.295, atol=0.001)

    print(f"All checks passed on {n_tests} random chromosomes: angles stay inside the limits, "
          f"every right leg mirrors its left partner half a cycle later, "
          f"and the standing chromosome puts all eight feet at z = {feet_z[0]:.3f}.")


if __name__ == "__main__":
    from chromosome import random_chromosome
    check_decode()
    animate(decode(random_chromosome()))
