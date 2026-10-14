"""
kinematics.py - Python translation of the lecturer's forward_leg_kinematics2.m

Given where a leg is attached to the body and its three joint angles,
work out the 3D position of each joint along the leg:

    j1 = leg base (on the body)
    j2 = end of hip
    j3 = end of knee
    j4 = end of foot

All angles are in radians.
"""

import numpy as np


# --- Helper function: axis-angle rotation matrix ---
def axis_angle_rotation_matrix(axis, angle):
    """Return the 3x3 matrix that rotates a vector by `angle` radians
    around `axis` (Rodrigues' rotation formula)."""
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)        # make it a unit vector
    x, y, z = axis
    c = np.cos(angle)
    s = np.sin(angle)
    C = 1 - c
    R = np.array([
        [x * x * C + c,     x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, y * y * C + c,     y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, z * z * C + c],
    ])
    return R


# --- Helper function: rotate a vector around an axis by an angle ---
def rotate_vector(v, axis, angle):
    """Rotate vector v around `axis` by `angle` radians.
    MATLAB's (R * v')' becomes R @ v for a 1D NumPy array."""
    R = axis_angle_rotation_matrix(axis, angle)
    return R @ v


def forward_leg_kinematics2(base_pos, base_angle, joint_angles, segment_lengths):
    """
    base_pos:        [x, y, z] position of leg base on body
    base_angle:      angle around body ellipse where leg base is located (radians)
    joint_angles:    [theta1, theta2, theta3] joint angles for the leg (radians)
    segment_lengths: [coxa, femur, tibia] lengths of leg segments

    Returns j1, j2, j3, j4: four NumPy arrays, each [x, y, z].
    """
    # Unpack joint angles
    theta1, theta2, theta3 = joint_angles   # coxa yaw, femur pitch, tibia pitch

    # Unpack segment lengths
    L1, L2, L3 = segment_lengths            # coxa, femur, tibia lengths

    z_axis = np.array([0.0, 0.0, 1.0])      # vertical axis, MATLAB's [0 0 1]

    # Joint 1: leg base on body.
    # Converted to a NumPy array so all four outputs have the same type
    # (in MATLAB this was just j1 = base_pos).
    j1 = np.array(base_pos, dtype=float)

    # --- Compute coxa direction with elevation ---
    coxa_elevation = np.deg2rad(30)         # fixed 30 degree upward pitch for coxa

    # Horizontal direction of coxa in XY plane based on base_angle + theta1
    coxa_horiz_dir = np.array([np.cos(base_angle + theta1),
                               np.sin(base_angle + theta1),
                               0.0])

    # Rotation axis for pitch up: perpendicular to coxa horizontal direction in XY plane
    rot_axis = np.cross(coxa_horiz_dir, z_axis)

    # Rotate horizontal coxa direction upward by coxa_elevation
    R = axis_angle_rotation_matrix(rot_axis, coxa_elevation)
    coxa_dir = R @ coxa_horiz_dir

    # Joint 2 position: end of coxa segment
    j2 = j1 + L1 * coxa_dir

    # --- Femur rotation ---
    # Femur pitch is relative to coxa direction: rotate around the axis
    # perpendicular to coxa_dir and the vertical axis.
    femur_rot_axis = np.cross(coxa_dir, z_axis)
    femur_rot_axis = femur_rot_axis / np.linalg.norm(femur_rot_axis)

    # Femur direction starts aligned with coxa_dir, then rotated by theta2
    femur_dir = rotate_vector(coxa_dir, femur_rot_axis, theta2)

    # Joint 3 position: end of femur segment
    j3 = j2 + L2 * femur_dir

    # --- Tibia rotation ---
    # Tibia pitch is relative to femur direction: rotate around the axis
    # perpendicular to femur_dir and the vertical axis.
    tibia_rot_axis = np.cross(femur_dir, z_axis)
    tibia_rot_axis = tibia_rot_axis / np.linalg.norm(tibia_rot_axis)

    # Tibia direction vector
    tibia_dir = rotate_vector(femur_dir, tibia_rot_axis, theta3)

    # Joint 4 position: end of tibia segment (foot)
    j4 = j3 + L3 * tibia_dir

    return j1, j2, j3, j4


if __name__ == "__main__":
    # Quick test: foot (last point) should be roughly [4.897, 0, 2.25]
    print(forward_leg_kinematics2([1, 0, 0], 0, [0, 0, 0], [1, 1.5, 2]))