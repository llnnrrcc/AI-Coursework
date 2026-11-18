# Contribution sheet


## Who did what

| Task | Sujan | Jake | Lauren | Maria |
| --- | :---: | :---: | :---: | :---: |
| **Part 1: model and limits** | | | | |
| Repo and environment setup, `requirements.txt` | | | ✓ | |
| Forward kinematics (`kinematics.py`) | | | | |
| Spider model and plotting (`spider_model.py`) | ✓ | | ✓ | |
| Coxa limits (`coxa_limits.md`) | | | ✓ | |
| Coxa symmetry (`coxa_symmetry.md`) | | | | |
| Femur limits (`femur_limits.md`) | | | | |
| Tibia limits (`tibia_limits.md`) | ✓ | | | |
| Floor height and standing pose | ✓ | | | |
| Combined joint limits (`joint_limits_summary.md`) | | | ✓ | |
| **Part 1: chromosome and GA** | | | | |
| Chromosome design (wave encoding, `DECISIONS.md` section 3) | ✓ | | | |
| Chromosome layout and decoding (`chromosome.py`, `gait.py`) | | | | |
| Genetic operators and their tests (`operators.py`, `test_operators.py`) | | | | |
| GA loop, selection and elitism (`ga.py`) | | | ✓ | |
| Repeatable seeded runs | | | ✓ | |
| **Part 1: fitness** | | | | |
| Support, lift and below-floor terms | ✓ | | | |
| Forward, too-high and crowding terms | ✓ | | | |
| Energy term | ✓ | | | |
| Finding and fixing loopholes (sinking, legs in the air, forward at 0, lazy back legs) | ✓ | | ✓ | |
| Fitness checks (`check_fitness()`) | ✓ | | | |
| Fitness write-up (`fitness_design.md`) | ✓ | | | |
| **Part 1: experiments and results** | | | | |
| GA settings experiments (`experiments.py`, `experiments.md`) | ✓ | | | |
| Final GA run and settings | ✓ | | ✓ | |
| Fitness graph (`fitness_graph.py`) | | | | |
| Saving results and foot-height plots (`save_results.py`, `foot_heights.py`) | | | | |
| Gait animation (`show_best.py`) | | | ✓ | |
| **Part 2: neural network** | | | | |
| Network from scratch: forward pass, backpropagation, gradient check (`nn/network.py`) | | | ✓ | |
| Training data (`nn/data.py`) | | | | |
| Training script (`nn/train.py`) | ✓ | | | |
| Learning-rate experiments (`nn/learning_rates.py`) | ✓ | | | |
| Architecture comparison (`nn/architectures.py`) | | | ✓ | |
| Held-out test (`nn/held_out_test.py`) | | | ✓ | |
| Network size check over 3 seeds (`nn/size_check.py`) | | | ✓ | |
| Architecture write-up (`nn/architectures.md`) | | | ✓ | |
| Network gait animation (`nn/show_nn_gait.py`) | | | ✓ | |
| Training write-up (`nn/training.md`) | ✓ | | | |
| Reflection (`nn/reflection.md`) | ✓ | | | |
| **Documentation and coordination** | | | | |
| Design decisions (`DECISIONS.md`) | ✓ | | ✓ | |
| README and how to run the code | ✓ | | | |
| Contribution sheet and AI-use statement | ✓ | | | |
| Planning, meetings and task lists | ✓ | ✓ | ✓ | ✓ |

## Agreed split

| Member | Student number | Contribution (%) |
| --- | --- | --- |
| Sujan | 2270752 | 25% |
| Jake | | 25% |
| Lauren | | 25% |
| Maria | | 25% |

Agreed by: Sujan [ ✓ ], Jake [ ✓ ], Lauren [ ✓ ], Maria [ ✓ ]

## Use of AI

[To be added once the group agrees the AI-use statement.]
