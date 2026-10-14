import numpy as np
import matplotlib.pyplot as plt
from kinematics import forward_leg_kinematics2

# --- Spider parameters (from plot_spider_pose.m) ---
N_LEGS = 8
SEGMENT_LENGTHS = np.array([1.2, 0.7, 1.0])   # [coxa, femur, tibia]
BODY_A = 1.5                                    # body oval half-length (front to back)
BODY_B = 1.0                                    # body oval half-width (side to side)

# Where each leg attaches around the body, in order L1, L2, L3, L4, R4, R3, R2, R1
BASE_ANGLES = np.deg2rad([45, 75, 105, 135, -135, -105, -75, -45])
LEG_LABELS = ["L1", "L2", "L3", "L4", "R4", "R3", "R2", "R1"]

def spider_joints(angles):
    """
    angles: 24 joint angles in radians, three per leg, in leg order L1 ... R1
    Returns a list of 8 legs, each a tuple (j1, j2, j3, j4) of [x, y, z] points.
    No plotting here, so the GA can call this quickly thousands of times.
    """
    legs = []
    for i in range(N_LEGS):
        # This leg's three angles (Python counts from 0, so leg i starts at i * 3)
        theta1 = angles[i * 3]
        theta2 = angles[i * 3 + 1]
        theta3 = angles[i * 3 + 2]

        # Where the leg joins the body: a point on the oval at this leg's angle
        angle = BASE_ANGLES[i]
        base_pos = [BODY_A * np.cos(angle), BODY_B * np.sin(angle), 0]

        # Pair A's function works out the four joint positions for this leg
        joints = forward_leg_kinematics2(base_pos, angle,
                                         [theta1, theta2, theta3], SEGMENT_LENGTHS)
        legs.append(joints)
    return legs

def draw_legs(ax, angles):
    """Draw all eight legs onto an existing 3D graph `ax`."""
    for j1, j2, j3, j4 in spider_joints(angles):
        # Coxa (body to first joint) in black
        ax.plot([j1[0], j2[0]], [j1[1], j2[1]], [j1[2], j2[2]], color="black", linewidth=2)
        # Femur (middle segment) in blue
        ax.plot([j2[0], j3[0]], [j2[1], j3[1]], [j2[2], j3[2]], color="blue", linewidth=2)
        # Tibia (outer segment) in red
        ax.plot([j3[0], j4[0]], [j3[1], j4[1]], [j3[2], j4[2]], color="red", linewidth=2)
        # Foot as a red dot
        ax.scatter(j4[0], j4[1], j4[2], color="red", s=20)

def plot_spider_pose(angles):
    # Define the spider's body dimensions
    a = 1.5
    b = 1.0

    # Create a 3D figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Calculate points around the oval body
    t = np.linspace(0, 2 * np.pi, 100)

    body_x = a * np.cos(t)
    body_y = b * np.sin(t)
    body_z = np.zeros_like(t)

    # Draw the oval
    ax.plot(body_x, body_y, body_z, color="black", linewidth=3)


    # Mark the front of the spider with a red triangle
    ax.scatter(a + 0.2, 0, 0, color="red", marker="^", s=80)

    # Define the angles where the eight legs attach
    left_leg_angles = np.deg2rad([45, 75, 105, 135])
    right_leg_angles = np.deg2rad([-135, -105, -75, -45])

    base_angles = np.concatenate((left_leg_angles, right_leg_angles))

    # Labels for each leg
    leg_labels = ["L1", "L2", "L3", "L4", "R4", "R3", "R2", "R1"]

    # Calculate and draw each leg's attachment point
    for i in range(8):
        angle = base_angles[i]

        x_base = a * np.cos(angle)
        y_base = b * np.sin(angle)

        ax.scatter(x_base, y_base, 0, color="blue", s=30)

        ax.text(x_base, y_base, 0.1, leg_labels[i])

    draw_legs(ax, angles)
    # Label the axes
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_zlim(-2, 2)

    plt.show()


if __name__ == "__main__":
    legs = spider_joints(np.zeros(24))
    for label, joints in zip(LEG_LABELS, legs):
        print(label, np.round(joints[3], 3))
    test = np.zeros(24)
    test[1], test[2] = -0.8, -1.2   # bend L1's femur and tibia down
    plot_spider_pose(test)
#empty
