"""Python port of the provided MATLAB spider model (provided/*.m).

Leg order matches plot_spider_pose.m: L1, L2, L3, L4, R4, R3, R2, R1.
A pose is a length-24 vector: [theta1, theta2, theta3] per leg, in radians.
"""
import numpy as np

N_LEGS = 8
N_JOINTS = 3 * N_LEGS
SEGMENT_LENGTHS = np.array([1.2, 0.7, 1.0])  # coxa, femur, tibia
BODY_A, BODY_B = 1.5, 1.0                     # body ellipse semi-axes
COXA_ELEVATION = np.deg2rad(30.0)
LEG_LABELS = ["L1", "L2", "L3", "L4", "R4", "R3", "R2", "R1"]
BASE_ANGLES = np.deg2rad([45, 75, 105, 135, -135, -105, -75, -45])
BASE_POS = np.stack([BODY_A * np.cos(BASE_ANGLES),
                     BODY_B * np.sin(BASE_ANGLES),
                     np.zeros(N_LEGS)], axis=1)


def _rotation_matrix(axis, angle):
    """Rodrigues rotation matrix (same convention as the MATLAB helper)."""
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s = np.cos(angle), np.sin(angle)
    C = 1.0 - c
    return np.array([
        [x * x * C + c,     x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, y * y * C + c,     y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, z * z * C + c],
    ])


def _rotate(v, axis, angle):
    return _rotation_matrix(axis, angle) @ v


def leg_kinematics(base_pos, base_angle, joint_angles, seg=SEGMENT_LENGTHS):
    """Return joint positions j1..j4 (4x3) for one leg."""
    t1, t2, t3 = joint_angles
    up = np.array([0.0, 0.0, 1.0])

    j1 = np.asarray(base_pos, dtype=float)
    horiz = np.array([np.cos(base_angle + t1), np.sin(base_angle + t1), 0.0])
    coxa_dir = _rotate(horiz, np.cross(horiz, up), COXA_ELEVATION)
    j2 = j1 + seg[0] * coxa_dir

    femur_axis = np.cross(coxa_dir, up)
    femur_dir = _rotate(coxa_dir, femur_axis / np.linalg.norm(femur_axis), t2)
    j3 = j2 + seg[1] * femur_dir

    tibia_axis = np.cross(femur_dir, up)
    n = np.linalg.norm(tibia_axis)
    if n < 1e-9:  # femur exactly vertical: axis undefined, fall back to coxa's
        tibia_axis, n = femur_axis, np.linalg.norm(femur_axis)
    tibia_dir = _rotate(femur_dir, tibia_axis / n, t3)
    j4 = j3 + seg[2] * tibia_dir
    return np.stack([j1, j2, j3, j4])


def pose_kinematics(angles):
    """angles: (24,) -> joint positions (8, 4, 3)."""
    angles = np.asarray(angles, dtype=float).reshape(N_LEGS, 3)
    return np.stack([leg_kinematics(BASE_POS[i], BASE_ANGLES[i], angles[i])
                     for i in range(N_LEGS)])


def foot_positions(angles):
    """angles: (24,) -> foot (j4) positions (8, 3)."""
    return pose_kinematics(angles)[:, 3, :]
