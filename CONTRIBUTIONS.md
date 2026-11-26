# Contribution sheet


## Who did what

| Task | up2270752 | up2274964 | up2277376 | up2305949 |
| --- | :---: | :---: | :---: | :---: |
| **Part 1: model and limits** | | | | |
| Repo and environment setup, `requirements.txt` | | ✓ | ✓ | ✓ |
| Forward kinematics (`kinematics.py`) | | ✓ | | |
| Spider model and plotting (`spider_model.py`) | ✓ | ✓ | ✓ | ✓ |
| Coxa limits (`coxa_limits.md`) | | | ✓ | |
| Coxa symmetry (`coxa_symmetry.md`) | | | | ✓ |
| Femur limits (`femur_limits.md`) | | ✓ | | |
| Tibia limits (`tibia_limits.md`) | ✓ | | | |
| Floor height and standing pose | ✓ | ✓ | | |
| Combined joint limits (`joint_limits/README.md`) | | | ✓ | |
| **Part 1: chromosome and GA** | | | | |
| Chromosome design (wave encoding, `DECISIONS.md` section 3) | ✓ | ✓ | | ✓ |
| Chromosome layout and decoding (`chromosome.py`, `gait.py`) | | ✓ | | |
| Genetic operators and their tests (`operators.py`, `test_operators.py`) | | | | ✓ |
| GA loop, selection and elitism (`ga.py`) | | | ✓ | |
| Repeatable seeded runs | | | ✓ | ✓ |
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
| Fitness graph (`fitness_graph.py`) | | | | ✓ |
| Saving results and foot-height plots (`save_results.py`, `foot_heights.py`) | | ✓ | | |
| Visualisation write-up (`visualisation.md`) | | ✓ | | |
| Gait animation (`show_best.py`) | | | ✓ | |
| **Part 2: neural network** | | | | |
| Network from scratch: forward pass, backpropagation, gradient check (`nn/network.py`) | | | ✓ | |
| Training data (`nn/data.py`) | | | | ✓ |
| Training script (`nn/train.py`) | ✓ | | | |
| Learning-rate experiments (`nn/learning_rates.py`) | ✓ | | | |
| Architecture comparison (`nn/architectures.py`) | | | ✓ | |
| Held-out test (`nn/held_out_test.py`) | | | ✓ | |
| Network size check over 3 seeds (`nn/size_check.py`) | | | ✓ | |
| Architecture write-up (`nn/architectures.md`) | | | ✓ | |
| Network gait animation (`nn/show_nn_gait.py`) | | | ✓ | |
| Training write-up (`nn/training.md`) | ✓ | | | |
| Reflection (`nn/reflection.md`) | ✓ | | | |
| PyTorch comparison implementation (`nn/pytorch_compare.py`) | | | | ✓ |
| PyTorch experiments and comparison graph (`nn/pytorch_comparison.png`) | | | | ✓ |
| PyTorch comparison write-up (`nn/pytorch_comparison.md`) | | | | ✓ |
| **Documentation and coordination** | | | | |
| Design decisions (`DECISIONS.md`) | ✓ | ✓ | ✓ | ✓ |
| README and how to run the code | ✓ | ✓ | | |
| Contribution sheet and AI-use statement | ✓ | | | |
| Planning, meetings and task lists | ✓ | ✓ | ✓ | ✓ |

## Agreed split

| Student number | Contribution (%) |
| --- | --- |
| up2270752 | 25% |
| up2274964 | 25% |
| up2277376 | 25% |
| up2305949 | 25% |

Agreed by: up2270752 [ ✓ ], up2274964 [ ✓ ], up2277376 [ ✓ ], up2305949 [ ✓ ]

## Use of AI

We used Claude (Anthropic's AI assistant) throughout. It explained concepts, suggested design options, wrote much of the code from our designs, ran some of the analyses, and drafted most of the write-ups, which we then checked and edited. It also helped plan the group's work.

We checked the work in three main ways. The backpropagation passes a gradient check (about 1e-11) and matches a PyTorch version of the same network (weights within 1.95e-13). The final GA run was re-run on a group member's own machine and gave the same numbers. Most other results were re-run by a group member; where Claude ran something that wasn't re-run, the table below says so.

The group made the final decisions: the fitness terms, the GA settings, the network design and what went in each write-up. Several of the key findings came from us watching the gaits rather than from the AI. One example is up2277376 spotting the lazy back legs, which led to the per-leg forward fix. The tables below show, file by file, what Claude did and what we did.

Each of us can explain the parts we worked on, as listed in the table above.

### File by file

| File | Who | What Claude did | What we did |
| --- | --- | --- | --- |
| `kinematics.py` | up2274964 | Ported the MATLAB leg kinematics to Python |
| `spider_model.py` | up2277376, up2305949 | Step-by-step guidance on the structure | Wrote and tested the model and the 3D plot |
| `joint_limits/coxa_limits.md` | up2277376 | Drafted the angle conversions and the wording of the results | up2277376 ran and checked every pose in the model |
| `joint_limits/femur_limits.md` | up2274964 | Ran the femur tests |
| `joint_limits/tibia_limits.md` | up2270752 | Drafted the reasoning behind the threshold | up2270752 checked it by running their own sweep |
| `joint_limits/coxa_symmetry.md` | up2305949 | Ran the symmetry tests |
| `joint_limits/README.md` | up2277376 | Combined the four results files | up2277376 checked the standing pose and the gaps between neighbouring feet by running the model |
| `DECISIONS.md` | Group | Proposed the wave-based chromosome; ran the cycle and floor numbers in the model; drafted section text | The group agreed and signed off the design and edited the text |
| `chromosome.py`, `gait.py` | up2274964 | Wrote the decoding and ran the decode checks |
| `fitness.py`, `fitness_design.md` | up2270752 | Proposed the first structure (support, lift, below floor) and helped write those terms and the hand-made test gaits; ran the loophole analysis and the seeded GA comparisons; re-scored the check table; helped write `check_fitness()`; proposed and tested the energy term and the per-leg forward fix | up2270752 wrote and ran the fitness function, added the later terms and re-ran every check on their own machine, and the numbers matched (2.354 for the energy run, 2.227 for the final run) |
| `operators.py`, `test_operators.py`, `fitness_graph.py` | up2305949 | Wrote and tested the operators, including the configurable mutation step size |
| `ga.py`, `show_best.py` | up2277376 | Step-by-step code and explanations | up2277376 built and ran the GA, chose the final settings and did the final runs |
| `experiments.py`, `experiments.md` | up2270752 | Wrote `experiments.py`, including the crossover, selection and mutation step comparisons; helped draft the write-up from the results files | up2270752 ran every experiment and wrote up the findings |
| `save_results.py`, `foot_heights.py`, `visualisation.md` | up2274964 | Wrote both scripts, re-ran the two earlier faulty runs and drafted the write-up | up2274964 ran the scripts and checked the write-up |
| `README.md`, `requirements.txt` | up2274964, up2270752 | Wrote the setup and run instructions |
| `nn/network.py`, `nn/network_explained.md` | up2277376 | Provided the code one part at a time (layers, forward pass, backpropagation, gradient check, saving and loading) and explained each part; drafted the explanation | up2277376 built it in stages, ran every test including the gradient check, and checked and edited the explanation |
| `nn/data.py` | up2305949 | Step-by-step instructions, no code | up2305949 wrote and tested the data preparation |
| `nn/train.py`, `nn/learning_rates.py`, `nn/compare_training.py`, `nn/training.md` | up2270752 | Wrote `compare_training.py` and drafted its write-up [up2270752 to confirm the rest] | up2270752 trained the network, ran the activation and batch size comparisons, and ran the learning rate comparison on three seeds |
| `nn/architectures.py`, `nn/size_check.py`, `nn/held_out_test.py`, `nn/show_nn_gait.py`, `nn/architectures.md` | up2277376 | Wrote the scripts and helped structure the write-up | up2277376 ran the experiments, chose the network size and wrote the reasoning |
| `nn/reflection.md` | up2270752 | Drafted it from the group's results; measured the joint-limit errors and the forward gap on the trained network | up2270752 rewrote it |
| `nn/pytorch_compare.py`, `nn/pytorch_comparison.md` | up2305949 | up2305949 ran the comparison and wrote it up |
| `webots/`, Webots section of `nn/reflection.md` | up2277376, up2270752 | Wrote the controller (`gait_player.py`) and the export script for up2277376; corrected the knee directions after testing, found that the hip motors were too weak, added the hip fan, the foot levelling and the swing lift test, ran most of the Webots tests on up2270752's machine and drafted the results | up2277376 set up the files for the module's Webots world; up2270752 ran simulations, checked the results and spotted the legs passing through each other, the back legs tangling, the hovering third pair and the dragging front foot |

### Ideas that came from Claude, and how we checked them

| Idea or finding | Where it came from | How we checked it |
| --- | --- | --- |
| Joint limits per leg from Wang et al. (2011) | Our own research; Claude helped us read the paper | up2277376 tested every coxa limit in the model |
| Wave-based chromosome (centre, size and timing for each joint) | Proposed by Claude | The group agreed it, and up2274964 ran the decode checks |
| Fixed leg teams, with the right legs copying the left | Proposed by Claude, based on Wang et al. | The group signed it off. Claude made one mistake about the distance between neighbouring legs, which we found and corrected on 11 November |
| Tournament selection and elitism | up2277376 chose them after Claude explained the options | up2277376's GA runs |
| Sinking loophole (feet sank under the floor instead of lifting) | Found in Claude's foot-by-foot breakdown of up2277376's run | up2277376 applied the fix and re-ran the GA |
| Hovering legs, and the forward score stopping at 0 | Found in Claude's breakdown; Claude proposed and tested the fixes | up2270752 applied them, and up2277376 confirmed the numbers matched |
| Energy term | up2277376 questioned leaving it out; Claude proposed and tested it | The group agreed, and up2270752's run matched the test exactly |
| Lazy back legs (some legs pushing for the others) | up2277376, by watching the animation | Claude measured each leg and tested the per-leg fix; up2277376 applied it |
| Held-out test (train on even frames, test on odd frames) | Proposed by Claude | up2277376 ran it |
| Final network size [2, 16, 24] | Claude reviewed 16 against 32 hidden neurons | up2277376's size check over three seeds decided it |

### Planning

Claude also helped up2277376 organise the group's work. It explained the brief and the marking scheme, wrote task lists for each of us, reviewed each push to GitHub, kept a log of our decisions, and explained Git and the Python setup. None of this is in the submitted code, but it shaped how we split the work.
