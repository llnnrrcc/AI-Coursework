"""Prints every foot z and reach in the tables of tibia_limits.md, for leg L1.

Run from the main repo folder: python joint_limits/check_tibia.py
Reach is the horizontal distance from the leg's base on the body to the foot.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spider_model import spider_joints


def l1_foot(femur, tibia, coxa=0.0):
    angles = np.zeros(24)
    angles[0:3] = [coxa, femur, tibia]
    base, _, _, foot = spider_joints(angles)[0]
    return foot[2], np.hypot(foot[0] - base[0], foot[1] - base[1])


print("Narrowing the edges (femur -0.8):")
for tibia in (-1.6, -1.7, -1.8):
    print("  tibia %.1f: z %.3f, reach %.2f" % ((tibia,) + l1_foot(-0.8, tibia)))

print("Femur sweep and final check (z / reach):")
for femur in (-0.5, -0.35, -0.2, -0.1, 0.0):
    cells = ["%.1f: %.3f / %.2f" % ((tibia,) + l1_foot(femur, tibia))
             for tibia in (-2.0, -1.9, -1.8, -1.7, -1.5, -1.4, -1.0, -0.5, 0.0)]
    print("  femur %5.2f | %s" % (femur, " | ".join(cells)))
