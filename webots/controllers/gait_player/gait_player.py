"""
gait_player.py - Webots controller that plays our GA gait on the provided SpiderOctopod.

Based on the module's demo controller (my_controller_s.py): it finds the same 24 motors and
starts from the same standing pose. It then plays gait.csv (made by webots/export_gait.py)
frame by frame, in a loop, and records where the body goes using the robot's GPS.

Our model and the Webots robot measure angles differently, so every angle is converted:

    webots angle = webots standing angle + SIGN x SCALE x (our angle - our standing angle)

The standing poses line up, and each joint moves away from standing the same amount as in
our gait. SIGN fixes joints that turn the other way on the Webots robot; it is checked one
joint at a time with MODE = "test" (see webots/README.md).

MODE = "play": stand, then play the gait for PLAY_SECONDS and report how far the body moved.
MODE = "test": stand, then run the six sign checks in TESTS one after another, on a loop.
"""

import csv
import math
import os

from controller import Robot

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

MODE = "play"            # "play" or "test"
TEST_SWING = 1.0         # how far the tested joint swings (rad); big enough to see

SECONDS_PER_STEP = 2.0   # our gait has 5 steps of 60 frames; 2 s per step keeps every
FRAMES_PER_STEP = 60     # joint under 1.2 rad/s, below the motors' 2.0 rad/s limit
PLAY_SECONDS = 30.0      # how long to walk before reporting the distance
MOTOR_VELOCITY = 2.0     # the motors' maximum speed (from SpiderOctopod.proto)

LEGS = ["L1", "L2", "L3", "L4", "R1", "R2", "R3", "R4"]
JOINTS = {"hip": "hip_joint", "thigh": "thigh_joint", "knee": "knee_joint"}

# Standing pose of the Webots robot (from the demo controller).
WEBOTS_STAND = {
    "L": {"hip": 0.0, "thigh": -1.07, "knee": 0.58},
    "R": {"hip": 0.0, "thigh": 1.07, "knee": -0.58},
}

# Standing pose of our model, per leg (coxa at the middle of each leg's range, femur -0.4,
# tibia -1.5; DECISIONS.md section 2).
OUR_STAND = {
    "L1": {"hip": -0.31, "thigh": -0.4, "knee": -1.5},
    "L2": {"hip": -0.32, "thigh": -0.4, "knee": -1.5},
    "L3": {"hip": -0.08, "thigh": -0.4, "knee": -1.5},
    "L4": {"hip": 0.31, "thigh": -0.4, "knee": -1.5},
    "R1": {"hip": 0.31, "thigh": -0.4, "knee": -1.5},
    "R2": {"hip": 0.32, "thigh": -0.4, "knee": -1.5},
    "R3": {"hip": 0.08, "thigh": -0.4, "knee": -1.5},
    "R4": {"hip": -0.31, "thigh": -0.4, "knee": -1.5},
}

# Which way each Webots joint turns compared with ours. Checked on 26 Nov with MODE = "test"
# and against the joint axes in SpiderOctopod.proto; both knees were flipped. In our model:
#   hip (coxa) +   : left feet swing backwards, right feet swing forwards
#   thigh (femur) +: the foot lifts up
#   knee (tibia) + : the lower leg straightens (foot lifts and moves outwards)
SIGN = {
    "L": {"hip": 1.0, "thigh": 1.0, "knee": 1.0},     # knee flipped after test: -1.0 stalled and lifted the body
    "R": {"hip": 1.0, "thigh": -1.0, "knee": -1.0},   # knee flipped after test: 1.0 stalled and lifted the body
}

# Our model's legs fan out round the body (BASE_ANGLES in spider_model.py), but the Webots
# legs all stand straight out sideways in two rows, so neighbouring legs can tangle. With
# HIP_FAN = True, each Webots hip stands at its leg's angle in our model instead of 0:
# front legs angled forwards, back legs backwards. The tilted Webots hip axis makes the
# fan narrower than ours, but it roughly doubles the gap between neighbouring feet.
HIP_FAN = True
BASE_ANGLES = {"L1": 45, "L2": 75, "L3": 105, "L4": 135,
               "R1": -45, "R2": -75, "R3": -105, "R4": -135}   # degrees, from spider_model.py

# Turning a hip about the tilted Webots axis also lowers the foot, so the fan alone leaves
# the front and back feet 0.175 m below the third pair, which then hover. These thigh lifts
# (our + = up, in rad) put every foot back at the height it has with the hips at 0. Found by
# forward kinematics of the legs in SpiderOctopod.proto; the left and right sides mirror.
FAN_THIGH_LIFT = {"1": 0.365, "2": 0.079, "3": 0.007, "4": 0.365}


def stand_angle(leg, joint):
    """The Webots angle this joint holds when our model is in its standing pose."""
    side = leg[0]
    if joint == "hip" and HIP_FAN:
        sideways = 90 if side == "L" else -90   # a leg pointing straight out
        fan = math.radians(BASE_ANGLES[leg] - sideways) + OUR_STAND[leg]["hip"]
        return SIGN[side]["hip"] * fan
    if joint == "thigh" and HIP_FAN:
        return WEBOTS_STAND[side]["thigh"] + SIGN[side]["thigh"] * FAN_THIGH_LIFT[leg[1]]
    return WEBOTS_STAND[side][joint]


# Our feet only rise about 0.2 above the contact line, and the shorter Webots legs turn the
# same knee movement into an even smaller lift, so the front feet drag. While a foot is in
# the air in our model (above BAND_HIGH), its Webots thigh is lifted by SWING_LIFT rad per
# metre of our foot's height above the line. 0 turns this off.
BAND_HIGH = -0.25        # our contact line (fitness.py)
SWING_LIFT = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0}   # per leg pair. Lifting feet clear walks less far:
# 1.5 on every pair walked 6.69 m and 1.5 on the front pair only 4.04 m, against 8.72 m with none.


# Our leg segments (1.2, 0.7, 1.0) are longer than the robot's (0.5, 0.6, 0.7). 1.0 copies
# our angles exactly; lower values make smaller movements if the robot tips over.
SCALE = {"hip": 1.0, "thigh": 1.0, "knee": 1.0}


# ---------------------------------------------------------------------------
# Set-up
# ---------------------------------------------------------------------------

robot = Robot()
timestep = int(robot.getBasicTimeStep())

gps = robot.getDevice("gps")
gps.enable(timestep)

motors = {}
for leg in LEGS:
    for joint, suffix in JOINTS.items():
        motor = robot.getDevice(f"{leg}_{suffix}")
        if motor is None:
            print(f"WARNING: motor {leg}_{suffix} not found")
            continue
        motor.setVelocity(MOTOR_VELOCITY)
        motors[(leg, joint)] = motor


def set_joint(leg, joint, angle):
    """Send one angle to one motor, kept inside the motor's limits."""
    motor = motors[(leg, joint)]
    low, high = motor.getMinPosition(), motor.getMaxPosition()
    if low < high:   # Webots reports 0, 0 when a motor has no limits
        angle = min(max(angle, low), high)
    motor.setPosition(angle)


def to_webots(leg, joint, our_angle):
    """Convert one of our angles to the Webots robot's convention."""
    side = leg[0]
    change = our_angle - OUR_STAND[leg][joint]
    return stand_angle(leg, joint) + SIGN[side][joint] * SCALE[joint] * change


def wait(seconds):
    """Run the simulation for a while without changing the targets."""
    for _ in range(int(seconds * 1000 / timestep)):
        if robot.step(timestep) == -1:
            raise SystemExit


def stand():
    for leg in LEGS:
        for joint in JOINTS:
            set_joint(leg, joint, stand_angle(leg, joint))
    wait(3.0)


def load_gait():
    """Read gait.csv into a list of frames, each a dict {(leg, joint): angle}."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gait.csv")
    names = {suffix: joint for joint, suffix in JOINTS.items()}
    frames = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            frame = {}
            for column, value in row.items():
                leg, suffix = column.split("_", 1)
                frame[(leg, names.get(suffix, suffix))] = float(value)   # foot_z kept as is
            frames.append(frame)
    return frames


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

# The six sign checks, in order: (leg, joint, what the foot should do, swing in our angles)
TESTS = [
    ("L1", "hip", "swing BACKWARDS (towards the rear)", TEST_SWING),
    ("L1", "thigh", "LIFT UP", TEST_SWING),
    ("L1", "knee", "STRAIGHTEN (foot moves up and outwards)", TEST_SWING),
    ("R1", "hip", "swing FORWARDS (towards the front)", TEST_SWING),
    ("R1", "thigh", "LIFT UP", TEST_SWING),
    ("R1", "knee", "STRAIGHTEN (foot moves up and outwards)", TEST_SWING),
]
HIP_TEST_LIFT = 0.5      # lift the thigh this much (our + = up) first, so the foot swings in the air


def test_joint():
    """Run each sign check in turn: swing the joint + from standing, then back. Loops forever."""
    while True:
        for number, (leg, joint, expected, swing) in enumerate(TESTS, start=1):
            side = leg[0]
            base = WEBOTS_STAND[side][joint]
            sensor = robot.getDevice(f"{leg}_{JOINTS[joint]}_sensor")   # reads the joint's real angle
            sensor.enable(timestep)
            print("")
            print(f"TEST {number}: {leg} {joint}. If SIGN is right, the foot should {expected}.")
            if joint == "hip":   # lift the foot off the floor so friction can't stop the swing
                set_joint(leg, "thigh", WEBOTS_STAND[side]["thigh"] + SIGN[side]["thigh"] * HIP_TEST_LIFT)
            wait(1.0)
            before = gps.getValues()
            target = base + SIGN[side][joint] * swing
            set_joint(leg, joint, target)
            # watch the joint every 0.5 s; a torque stuck at the motor's maxTorque means it is blocked
            motor = motors[(leg, joint)]
            motor.enableTorqueFeedback(timestep)
            thigh_sensor = robot.getDevice(f"{leg}_thigh_joint_sensor")
            thigh_sensor.enable(timestep)
            for _ in range(6):
                wait(0.5)
                print(f"      {joint} {sensor.getValue():+.3f} rad, torque {motor.getTorqueFeedback():+6.1f} N m, "
                      f"thigh {thigh_sensor.getValue():+.3f} rad")
            after = gps.getValues()
            # a foot pushed into the floor lifts the body (dz > 0); a lifted foot does not
            print(f"    target {target:+.3f} rad, reached {sensor.getValue():+.3f} rad; body moved "
                  f"dx {after[0] - before[0]:+.4f}  dy {after[1] - before[1]:+.4f}  dz {after[2] - before[2]:+.4f} m")
            set_joint(leg, joint, base)
            wait(1.0)
            set_joint(leg, "thigh", WEBOTS_STAND[side]["thigh"])
            wait(1.0)
            print("    back to standing")


def play():
    frames = load_gait()
    frame_seconds = SECONDS_PER_STEP / FRAMES_PER_STEP
    start = gps.getValues()
    print(f"Loaded {len(frames)} frames. Start position x={start[0]:.3f} y={start[1]:.3f} z={start[2]:.3f}")

    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webots_log.csv")
    with open(log_path, "w", newline="") as log_file:
        log = csv.writer(log_file)
        log.writerow(["time_s", "x", "y", "z"])
        t = 0.0
        next_report = 0.0
        while t < PLAY_SECONDS:
            frame = frames[int(t / frame_seconds) % len(frames)]
            for (leg, joint), angle in frame.items():
                if joint == "foot_z":
                    continue
                target = to_webots(leg, joint, angle)
                if joint == "thigh":
                    air = max(0.0, frame.get((leg, "foot_z"), BAND_HIGH) - BAND_HIGH)
                    target += SIGN[leg[0]]["thigh"] * SWING_LIFT[leg[1]] * air
                set_joint(leg, joint, target)
            if robot.step(timestep) == -1:
                return
            t += timestep / 1000
            x, y, z = gps.getValues()
            log.writerow([f"{t:.3f}", f"{x:.4f}", f"{y:.4f}", f"{z:.4f}"])
            if t >= next_report:
                print(f"t={t:5.1f}s  x={x:.3f}  y={y:.3f}  height={z:.3f}")
                next_report += SECONDS_PER_STEP

    end = gps.getValues()
    dx, dy = end[0] - start[0], end[1] - start[1]
    print("")
    print(f"After {PLAY_SECONDS:.0f} s: moved {dx:+.3f} m forwards (x) and {dy:+.3f} m sideways (y),")
    print(f"{math.hypot(dx, dy):.3f} m in total. Height went from {start[2]:.3f} to {end[2]:.3f} m.")
    print(f"Body position every timestep saved to {log_path}")
    stand()


stand()
if MODE == "test":
    test_joint()
else:
    play()
