"""
webots/export_gait.py - save the final GA gait as a CSV the Webots controller can read.

Run from the main repo folder:  python webots/export_gait.py

Writes webots/controllers/gait_player/gait.csv: 300 rows (frames) x 24 columns (joint
angles in radians, our own model's convention). Each column is named after the matching
Webots motor (coxa -> hip_joint, femur -> thigh_joint, tibia -> knee_joint), so the
controller needs no NumPy and none of our other code.
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # the main repo folder
from gait import decode

LEG_ORDER = ["L1", "L2", "L3", "L4", "R4", "R3", "R2", "R1"]   # decode() column order
JOINTS = ["hip_joint", "thigh_joint", "knee_joint"]             # coxa, femur, tibia

if __name__ == "__main__":
    angles = decode(np.load("final_best_chromosome.npy"))
    names = [f"{leg}_{joint}" for leg in LEG_ORDER for joint in JOINTS]
    out = os.path.join(os.path.dirname(__file__), "controllers", "gait_player", "gait.csv")
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(names)
        writer.writerows([[f"{a:.6f}" for a in row] for row in angles])
    print(f"Saved {angles.shape[0]} frames x {angles.shape[1]} angles to {out}")
