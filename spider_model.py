import numpy as np
import matplotlib.pyplot as plt
from kinematics import forward_leg_kinematics2

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


    # Label the axes
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_zlim(-2, 2)

    plt.show()


if __name__ == "__main__":
    plot_spider_pose(np.zeros(24))
