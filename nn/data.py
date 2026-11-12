
import numpy as np

from chromosome import joint_limits, standing_chromosome
from gait import decode

# Joint limits for all 8 legs
# Order: L1, L2, L3, L4, R4, R3, R2, R1
# Each leg contains: coxa, femur, tibia

LIMITS_LOW = []
LIMITS_HIGH = []

for leg in range(8):
    for joint in range(3):

        # Left legs: positions 0 to 3
        if leg < 4:
            minimum, maximum = joint_limits(leg, joint)

        # Right legs: mirror the corresponding left leg
        else:
            left_leg = 7 - leg
            minimum, maximum = joint_limits(left_leg, joint)

            # Coxa angles are reversed on the right
            if joint == 0:
                minimum, maximum = -maximum, -minimum

        LIMITS_LOW.append(minimum)
        LIMITS_HIGH.append(maximum)

LIMITS_LOW = np.array(LIMITS_LOW)
LIMITS_HIGH = np.array(LIMITS_HIGH)


def scale(angles):
    """Convert joint angles to values between 0 and 1."""
    return (angles - LIMITS_LOW) / (LIMITS_HIGH - LIMITS_LOW)

def unscale(values):
    """Convert scaled values back to joint angles."""
    return values * (LIMITS_HIGH - LIMITS_LOW) + LIMITS_LOW

def make_dataset(angles):
    """Create neural network inputs and target angles."""

    angles = np.asarray(angles, dtype=float)

    if angles.shape != (300, 24):
        raise ValueError("Expected angles with shape (300, 24)")

    # Frame numbers 0 to 299
    t = np.arange(300)

    # Five walking cycles across 300 frames
    phase = 2 * np.pi * 5 * t / 300

    # Neural network inputs: 2 numbers per frame
    inputs = np.column_stack((
        np.sin(phase),
        np.cos(phase)
    ))

    # Neural network targets: 24 angles per frame
    targets = scale(angles)

    return inputs, targets

if __name__ == "__main__":

    # Test 1: Standing chromosome
    chromosome = standing_chromosome()
    angles = decode(chromosome)

    inputs, targets = make_dataset(angles)

    print("Standing gait:")
    print("Input shape:", inputs.shape)
    print("Target shape:", targets.shape)

    assert inputs.shape == (300, 2)
    assert targets.shape == (300, 24)

    # Check all targets are between 0 and 1
    assert targets.min() >= -1e-10
    assert targets.max() <= 1 + 1e-10

    # Check scaling and unscaling return original angles
    assert np.allclose(unscale(scale(angles)), angles)

    print("Standing gait tests passed!")

    # Test 2: Random chromosome
    from chromosome import random_chromosome

    rng = np.random.default_rng(0)
    random_genes = random_chromosome(rng)

    random_angles = decode(random_genes)
    random_inputs, random_targets = make_dataset(random_angles)

    assert random_inputs.shape == (300, 2)
    assert random_targets.shape == (300, 24)

    assert random_targets.min() >= -1e-10
    assert random_targets.max() <= 1 + 1e-10

    assert np.allclose(
        unscale(scale(random_angles)),
        random_angles
    )

    print("Random gait tests passed!")
    print("All data preparation tests passed!")
