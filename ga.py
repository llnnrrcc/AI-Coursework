import numpy as np

from chromosome import N_GENES, LOW, HIGH, random_chromosome
from fitness import fitness
from operators import crossover, mutate
from fitness_graph import plot_fitness_history

# --- GA settings (change these to run experiments) ---
POPULATION_SIZE = 40    # how many chromosomes in each generation
GENERATIONS = 50        # how many times the main loop runs
MUTATION_RATE = 0.1     # chance of each gene changing, passed to mutate()
TOURNAMENT_SIZE = 3     # how many chromosomes compete in each selection
ELITE_COUNT = 2         # how many of the best are copied unchanged into the next generation

def initial_population(rng):
    """Create the first generation: POPULATION_SIZE random chromosomes, every gene inside its bounds."""
    population = [random_chromosome(rng) for _ in range(POPULATION_SIZE)]
    return np.array(population)

def evaluate(population):
    """Score every chromosome with fitness(). Returns one score per chromosome."""
    return np.array([fitness(chromosome) for chromosome in population])

def tournament_select(population, scores, rng):
    """Pick TOURNAMENT_SIZE chromosomes at random and return the one with the best score."""
    contestants = rng.choice(len(population), size=TOURNAMENT_SIZE, replace=False)
    winner = contestants[np.argmax(scores[contestants])]
    return population[winner]

def next_generation(population, scores, rng):
    """Make the next generation: keep the best ELITE_COUNT unchanged, fill the rest by breeding."""
    # Elitism: the best chromosomes go through untouched
    best_first = np.argsort(scores)[::-1]
    new_population = [population[i].copy() for i in best_first[:ELITE_COUNT]]

    # Breeding: select two parents, cross them over, mutate the children
    while len(new_population) < POPULATION_SIZE:
        parent1 = tournament_select(population, scores, rng)
        parent2 = tournament_select(population, scores, rng)
        child1, child2 = crossover(parent1, parent2)
        new_population.append(mutate(child1, MUTATION_RATE))
        if len(new_population) < POPULATION_SIZE:
            new_population.append(mutate(child2, MUTATION_RATE))

    return np.array(new_population)

if __name__ == "__main__":
    rng = np.random.default_rng(42)
    population = initial_population(rng)
    print(population.shape)
    print(np.all(population >= LOW), np.all(population <= HIGH))
    scores = evaluate(population)
    print(scores.shape, round(scores.max(), 3), round(scores.mean(), 3))
    winners = [tournament_select(population, scores, rng) for _ in range(1000)]
    print(round(evaluate(np.array(winners[:40])).mean(), 3))
    new_population = next_generation(population, scores, rng)
    new_scores = evaluate(new_population)
    print(new_population.shape, round(new_scores.max(), 3), round(new_scores.mean(), 3))

