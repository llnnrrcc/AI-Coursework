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

## Running each part

Run everything from the main repo folder, with the venv active. Scripts that
open a window (graphs, animations) carry on or finish when you close it.

### Checks

These test one piece of the code and print what they checked. Run them after
changing anything they cover.

| Command | What it checks and shows |
| --- | --- |
| `python kinematics.py` | Prints one leg's four joint positions; the foot should be about `[4.897 0. 2.25]`. |
| `python spider_model.py` | Prints every foot position with all angles at 0, then opens a 3D plot of the spider with L1 in the standing pose. |
| `python chromosome.py` | Prints the gene table: which genes belong to which joint, and each gene's range. Compare it with `DECISIONS.md` section 3. |
| `python gait.py` | Checks 100 random chromosomes stay inside the joint limits and that right legs mirror the left, then animates one random gait. |
| `python fitness.py` | Checks walking forwards scores above standing, and standing above walking backwards, then prints example scores and how long one call takes. |
| `python test_operators.py` | Checks crossover and mutation keep every gene inside its range and repeat exactly with the same seed. |
| `python -m nn.network` | Gradient check on the from-scratch backpropagation (should be about 1e-11), and checks a saved network loads back the same. Leaves a `test_model.npz` you can delete. |
| `python -m nn.data` | Checks the training data has the right shapes and scaling. |

### Part 1: genetic algorithm

| Command | What it does | Output |
| --- | --- | --- |
| `python ga.py` | Runs the GA with the settings at the top of `ga.py` (population 80, 100 generations, seed 1), printing the best and average fitness each generation. About 6 to 10 minutes. | Saves `best_chromosome.npy`, then opens the fitness graph. |
| `python show_best.py` | Animates the gait in `best_chromosome.npy`, so run `ga.py` first. | 3D animation window. |
| `python experiments.py` | Compares population size, mutation rate and tournament size, three seeds each. The runs are spread across your CPU cores, so it takes about 5 to 7 minutes on 16 cores and longer on fewer. For a quick test: `python experiments.py --generations 5 --seeds 1 --out test_run`. The crossover comparison on its own: `python experiments.py --only CROSSOVER --out experiment_results_crossover`. | A graph per setting and `summary.csv` in `experiment_results/`. The ones in the report are in `results/experiments/`. |
| `python foot_heights.py` | Redraws the foot height graphs of the two earlier faulty runs (sinking and hovering legs) used in `visualisation.md`. | `results/earlier_runs/foot_heights_*.png`. |
| `python save_results.py` | Saves the visuals of the final gait (`final_best_chromosome.npy`) for the report. The first run re-runs the GA to get its fitness history (about 6 to 10 minutes); after that it takes seconds. | `results/`: fitness graph and its CSV, a looping GIF of one step, side and top still poses, and a foot height graph. |

`final_best_chromosome.npy` is the gait from the final run, used in the report
and by the neural network. Running `ga.py` writes `best_chromosome.npy`
instead, so it never overwrites the final one.

### Part 2: neural network

The network learns the final GA gait in `final_best_chromosome.npy`.

| Command | What it does | Output |
| --- | --- | --- |
| `python -m nn.train` | Trains a [2, 16, 24] network for 2,000 epochs, printing the error every 100. | `nn/model.npz`, `nn/training_loss.png`, `nn/predicted_vs_real.png`. |
| `python -m nn.show_nn_gait` | Scores the trained network's gait with the GA's fitness function next to the GA's own, prints the angle error, then animates the network's gait. Needs `nn/model.npz`. | Printed comparison and an animation window. |
| `python -m nn.learning_rates` | Trains with learning rates 0.1, 0.5, 2.0 and 30.0 and compares the error curves. | `nn/learning_rates.png`. |
| `python -m nn.architectures` | Trains six network sizes and prints each one's final error, training time and gait fitness. | `nn/architectures.png`. |

The training scripts overwrite the files in `nn/` that the report uses. If you
are only experimenting, don't commit those files.

## Repo layout

| Path | Purpose |
| --- | --- |
| `provided/` | The lecturer's original MATLAB files. Read-only reference. |
| `kinematics.py` | Python translation of `forward_leg_kinematics2.m`. |
| `spider_model.py` | Spider body and legs in Python. |
| `chromosome.py` | Gene layout, gene ranges and joint limits. |
| `gait.py` | Turns a chromosome into 300 frames of joint angles; animation. |
| `fitness.py` | Fitness function for the GA. |
| `operators.py` | Crossover and mutation. |
| `ga.py` | Genetic algorithm: selection, elitism, main loop. |
| `fitness_graph.py` | Best and average fitness graph. |
| `show_best.py` | Animates the best gait from the last GA run. |
| `experiments.py` | GA settings experiments. |
| `save_results.py` | Saves the report visuals into `results/`. |
| `final_best_chromosome.npy` | The final evolved gait. |
| `nn/` | Neural network (Part 2), written from scratch. |
| `foot_heights.py` | Foot height through one step, used to catch hovering and sinking legs. |
| `results/` | Graphs and animation used in the report. `results/earlier_runs/` keeps the two faulty gaits from before the fitness fixes. |
| `DECISIONS.md` | Design decisions and rejected options. |
| `visualisation.md` | How the visuals were used to catch faults in the gait. |
| `fitness_design.md`, `experiments.md`, `nn/training.md` | Write-ups for each part. |
| `joint_limits`| Joint limit testing. |
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

If the code starts using a new package, add it to `requirements.txt` with its
version (`pip show <package>` gives the version). Only list packages the code
imports directly, not everything `pip freeze` shows; pip installs the rest
automatically.

## Team

| Pair | Members |
| --- | ---|
| A | up2270752, up2274964 |
| B | up2277376, up2305949 |
