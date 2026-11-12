
"""
Genetic operators for the spider gait genetic algorithm.

A chromosome has 36 genes, grouped into four legs.
Each leg has 9 genes (coxa, femur and tibia parameters).
"""

import numpy as np
from chromosome import N_GENES, LOW, HIGH


def crossover(p1, p2, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    """Create two children by exchanging complete leg blocks."""
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)

    if p1.shape != (N_GENES,) or p2.shape != (N_GENES,):
        raise ValueError("Each parent must contain 36 genes")

    # Copies ensure we do not change the original parents
    child1 = p1.copy()
    child2 = p2.copy()

    # Four left legs, nine genes per leg
    for leg in range(4):
        start = leg * 9
        end = start + 9

        # Randomly choose whether to swap this entire leg
        if rng.random() < 0.5:
            child1[start:end] = p2[start:end]
            child2[start:end] = p1[start:end]

    return child1, child2


def mutate(chromosome, rate, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    """Mutate genes while keeping all values within their bounds."""
    chromosome = np.asarray(chromosome, dtype=float)

    if chromosome.shape != (N_GENES,):
        raise ValueError("Chromosome must contain 36 genes")

    if not 0 <= rate <= 1:
        raise ValueError("Mutation rate must be between 0 and 1")

    mutated = chromosome.copy()

    for i in range(N_GENES):
        # Each gene has 'rate' probability of being changed
        if rng.random() < rate:

            # Small change relative to the gene's allowed range
            change = rng.normal(
                0, 0.05 * (HIGH[i] - LOW[i])
            )

            mutated[i] += change

            # Every third gene is a timing gene
            if i % 3 == 2:

                # Coxa timing belongs to the narrow
                # interval -0.125 to 0.125
                if (i // 3) % 3 == 0:
                    mutated[i] = np.clip(
                        mutated[i], LOW[i], HIGH[i]
                    )

                # Femur/tibia timing wraps around 0 to 1
                else:
                    mutated[i] = mutated[i] % 1.0

            # Centre and size genes stay inside bounds
            else:
                mutated[i] = np.clip(
                    mutated[i], LOW[i], HIGH[i]
                )

    return mutated
