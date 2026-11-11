"""
chromosome.py - the shape of a chromosome and the allowed range of every gene.

A chromosome is a NumPy array of 36 numbers: 9 genes per left leg, in the order
L1, L2, L3, L4. The right legs copy the left ones (see gait.py), so they have no
genes of their own.

Within each leg (positions 0-8):
    0, 1, 2   coxa  centre, size, timing
    3, 4, 5   femur centre, size, timing
    6, 7, 8   tibia centre, size, timing
So L1 is genes 0-8, L2 is 9-17, L3 is 18-26 and L4 is 27-35.

What each gene means (DECISIONS.md, section 3):
    centre  the middle of the joint's movement, anywhere inside the joint's limits
    size    how far the joint moves, as a fraction (0 to 1) of the room between
            the centre and the nearer limit
    timing  where in the cycle the movement happens, as a fraction of a cycle

Every gene has a fixed range (LOW to HIGH below), and gait.py builds the angles so
that any chromosome inside these ranges gives angles inside the joint limits.
"""

import numpy as np

N_LEGS = 4                     # left legs only; the right legs copy them
GENES_PER_JOINT = 3            # centre, size, timing
JOINTS_PER_LEG = 3             # coxa, femur, tibia
GENES_PER_LEG = GENES_PER_JOINT * JOINTS_PER_LEG    # 9
N_GENES = N_LEGS * GENES_PER_LEG                    # 36

LEG_NAMES = ["L1", "L2", "L3", "L4"]
JOINT_NAMES = ["coxa", "femur", "tibia"]

# Position of each gene inside its joint's group of three
CENTRE, SIZE, TIMING = 0, 1, 2

# --- Joint limits in radians (joint_limits_summary.md) ---
# The coxa limits differ per leg because each leg joins the body at a different
# angle. The right legs use the same limits with the sign flipped.
COXA_LIMITS = {
    "L1": (-0.62, 0.00),
    "L2": (-0.62, -0.01),
    "L3": (-0.54, 0.38),
    "L4": (0.14, 0.47),
}
FEMUR_LIMITS = (-0.5, -0.2)    # same for every leg
TIBIA_LIMITS = (-1.7, 0.0)     # same for every leg

# The coxa timing gene is only allowed to move an eighth of a cycle either side
# of its team's timing, so the GA can't move a leg into the other team.
COXA_TIMING_RANGE = (-0.125, 0.125)
FREE_TIMING_RANGE = (0.0, 1.0)     # femur and tibia can lift at any point in the step


def gene_index(leg, joint, gene):
    """Position in the 36-gene chromosome, e.g. gene_index(1, 2, SIZE) is L2's tibia size."""
    return leg * GENES_PER_LEG + joint * GENES_PER_JOINT + gene


def joint_limits(leg, joint):
    """(min, max) angle in radians for one joint of a left leg (leg 0-3, joint 0-2)."""
    if joint == 0:
        return COXA_LIMITS[LEG_NAMES[leg]]
    if joint == 1:
        return FEMUR_LIMITS
    return TIBIA_LIMITS


# --- LOW and HIGH: the allowed range of every gene ---
LOW = np.zeros(N_GENES)
HIGH = np.zeros(N_GENES)
for leg in range(N_LEGS):
    for joint in range(JOINTS_PER_LEG):
        # Centre: anywhere inside the joint's limits
        LOW[gene_index(leg, joint, CENTRE)], HIGH[gene_index(leg, joint, CENTRE)] = joint_limits(leg, joint)
        # Size: from not moving at all (0) to using all the room available (1)
        LOW[gene_index(leg, joint, SIZE)], HIGH[gene_index(leg, joint, SIZE)] = 0.0, 1.0
        # Timing: a narrow window for the coxa, a whole cycle for femur and tibia
        timing_range = COXA_TIMING_RANGE if joint == 0 else FREE_TIMING_RANGE
        LOW[gene_index(leg, joint, TIMING)], HIGH[gene_index(leg, joint, TIMING)] = timing_range


def random_chromosome(rng=None):
    """A chromosome with every gene drawn evenly from its range (for the starting population)."""
    rng = np.random.default_rng() if rng is None else rng
    return rng.uniform(LOW, HIGH)


def standing_chromosome():
    """
    The standing pose from DECISIONS.md section 2 as a chromosome: every centre at the
    standing pose and every size 0, so the spider stands still. Useful for testing.
    """
    standing_coxa = {"L1": -0.31, "L2": -0.32, "L3": -0.08, "L4": 0.31}
    c = np.zeros(N_GENES)
    for leg in range(N_LEGS):
        c[gene_index(leg, 0, CENTRE)] = standing_coxa[LEG_NAMES[leg]]
        c[gene_index(leg, 1, CENTRE)] = -0.4
        c[gene_index(leg, 2, CENTRE)] = -1.5
    return c


if __name__ == "__main__":
    # Print the gene table so it can be checked against DECISIONS.md
    print(f"N_GENES = {N_GENES}")
    for leg in range(N_LEGS):
        for joint in range(JOINTS_PER_LEG):
            i = gene_index(leg, joint, 0)
            print(f"{LEG_NAMES[leg]} {JOINT_NAMES[joint]:5s} genes {i:2d}-{i + 2:2d}  "
                  f"centre {LOW[i]:+.2f} to {HIGH[i]:+.2f}   size 0 to 1   "
                  f"timing {LOW[i + 2]:+.3f} to {HIGH[i + 2]:+.3f}")
