"""show_best.py - play the best chromosome from the last GA run as an animation."""

import numpy as np
from gait import decode, animate

best = np.load("best_chromosome.npy")
animate(decode(best))