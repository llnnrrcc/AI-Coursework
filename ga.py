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
        child1, child2 = crossover(parent1, parent2, rng)
        new_population.append(mutate(child1, MUTATION_RATE, rng))
        if len(new_population) < POPULATION_SIZE:
            new_population.append(mutate(child2, MUTATION_RATE, rng))

    return np.array(new_population)

def run_ga(seed=42):
    """Run the whole GA. Returns the best chromosome and the fitness history."""
    rng = np.random.default_rng(seed)
    population = initial_population(rng)
    best_history = []
    average_history = []

    for generation in range(GENERATIONS):
        scores = evaluate(population)
        best_history.append(scores.max())
        average_history.append(scores.mean())
        print(f"Generation {generation + 1}: best {scores.max():.3f}, average {scores.mean():.3f}")
        population = next_generation(population, scores, rng)

    # Score the final generation and save its best chromosome
    scores = evaluate(population)
    best = population[np.argmax(scores)]
    np.save("best_chromosome.npy", best)
    return best, best_history, average_history

if __name__ == "__main__":
    best, best_history, average_history = run_ga()
    plot_fitness_history(best_history, average_history)
