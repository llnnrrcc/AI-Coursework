# Contribution sheet

Draft for everyone to check. The brief asks for an agreed contribution sheet, so nothing here is final until all four of us have read our own row, corrected it, and agreed the split.

I built the first version from the git history (who added or changed each file) and from what we agreed in meetings. Commit counts aren't a fair measure on their own, because some commits are one-line fixes or line-ending changes and some are whole components, so the rows below list what each person built rather than how often they committed.

## Who did what

### Sujan (Pair A)

- Part 1 joint limits: tibia limits (`tibia_limits.md`), and the floor height and standing pose with Jake.
- Chromosome design: the wave encoding section of `DECISIONS.md` (36 genes, 5 cycles in 300 frames, the floor test).
- Fitness function (`fitness.py`, `fitness_design.md`): the support, lift and below-floor terms, the weights and their reasons, `check_fitness()`, adding the energy term, and the final 100-generation GA run.
- GA experiments: `experiments.py` (population, mutation rate and tournament size over three seeds, run in parallel) and the write-up in `experiments.md`.
- Part 2, covering Maria's training tasks: `nn/train.py`, `nn/learning_rates.py`, the learning-rate choice, `nn/training.md` and `nn/reflection.md`.

### Jake (Pair A)

- Part 1 joint limits: femur limits (`femur_limits.md`).
- Forward kinematics (`kinematics.py`).
- Chromosome layout and decoding: `chromosome.py` and `decode()` in `gait.py`.
- Results and visualisation: `save_results.py`, `foot_heights.py`, `visualisation.md` and the saved earlier runs in `results/earlier_runs/`.
- `README.md` and `requirements.txt`.

### Lauren (Pair B)

- Part 1 joint limits: coxa limits (`coxa_limits.md`).
- The GA itself (`ga.py`): initial population, tournament selection, elitism, the main loop, seeded runs and the final settings.
- Fitness fixes: the sinking fix, the per-leg forward fix (lazy back legs) and the energy term proposal.
- The network (`nn/network.py`): forward pass, backpropagation, gradient check, save and load.
- Network testing: `nn/architectures.py`, `nn/held_out_test.py`, `nn/show_nn_gait.py` and `show_best.py`.
- Most of `DECISIONS.md`.

### Maria (Pair B)

- Coxa symmetry (`coxa_symmetry.md`).
- Genetic operators (`operators.py`): leg-block crossover and bounded mutation, with tests in `test_operators.py`.
- The fitness graph (`fitness_graph.py`).
- Part 2 data preparation (`nn/data.py`): the sine and cosine inputs, target scaling and its tests.

## Agreed split

| Member | Contribution (%) |
| --- | --- |
| Sujan | |
| Jake | |
| Lauren | |
| Maria | |

Agreed by: Sujan [ ], Jake [ ], Lauren [ ], Maria [ ]

## Use of AI

[To be added once the group agrees the AI-use statement.]
