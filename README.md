# AI Coursework: Spider Kinematics with GAs and Neural Networks

Group coursework for M33174 Artificial Intelligence. Part 1 evolves a walking
gait for a 3D spider model using a genetic algorithm. Part 2 trains a neural
network, written from scratch, to generate the joint angles.

The spider has 8 legs with 3 joints each (coxa, femur, tibia), so a pose is a
vector of 24 angles in radians. Leg order is L1, L2, L3, L4, R4, R3, R2, R1.

## Setup

You need Python 3.11 or newer and Git. Check with `python --version`
(on Windows, `py --version` also works).

### 1. Clone the repo

```
git clone https://github.com/llnnrrcc/AI-Coursework.git
cd AI-Coursework
```

### 2. Create and activate a virtual environment

Windows (PowerShell):

```
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell says scripts are disabled, run this once and retry:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

macOS / Linux:

```
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now start with `(venv)`. If `python` is not recognised on
Windows, reinstall Python from python.org and tick "Add python.exe to PATH",
then restart VS Code. Do not keep the repo inside OneDrive; syncing the `venv`
folder causes problems.

### 3. Install the dependencies

```
pip install -r requirements.txt
```

### 4. Check it works

```
python kinematics.py
```

The last of the four printed points (the foot) should be about
`[4.897 0. 2.25]`.

In VS Code, if it doesn't pick up the environment, press Ctrl+Shift+P, choose
"Python: Select Interpreter", and pick the one inside `venv`.

## Repo layout

| Path | Purpose |
| --- | --- |
| `provided/` | The lecturer's original MATLAB files. Read-only reference. |
| `kinematics.py` | Python translation of `forward_leg_kinematics2.m`. |
| `spider_model.py` | Spider body and legs in Python. |
| `gait.py` | Gait chromosome decoder. |
| `fitness.py` | Fitness function for the GA. |
| `ga.py` | Genetic algorithm: selection, crossover, mutation, main loop. |
| `nn/` | Neural network (Part 2), written from scratch. |
| `data/` | Evolved gaits and training data. |
| `requirements.txt` | Python dependencies. |

## Git workflow

- Work on your pair's branch (`pair-a` or `pair-b`), not directly on `main`.
- Pull before you start: `git pull`.
- Commit small and often, with a message that says what changed.
- Merge into `main` through a pull request on GitHub, and have the other pair
  look at it first.
- Never commit `venv/`. It is already in `.gitignore`.
- If Git shows files as modified that you did not touch, it is probably line
  endings. Run `git config core.autocrlf true` once and do not commit them.

If you install a new package, update the dependency list before committing:

```
pip freeze > requirements.txt
```

## Team

| Pair | Members |
| --- | ---|
| A | up2270752, up2274964 |
| B | up2277376, up2305949 |
