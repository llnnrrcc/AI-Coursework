
import matplotlib.pyplot as plt


def plot_fitness_history(best_history, average_history):
    """Plot best and average fitness over generations."""

    if len(best_history) != len(average_history):
        raise ValueError("Fitness histories must have equal lengths")

    generations = range(1, len(best_history) + 1)

    plt.plot(generations, best_history, label="Best fitness")
    plt.plot(generations, average_history, label="Average fitness")

    plt.xlabel("Generation")
    plt.ylabel("Fitness score")
    plt.title("Genetic Algorithm Fitness Progress")
    plt.legend()
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    # Temporary test data until Lauren's GA is ready
    best = [10, 15, 21, 24, 30]
    average = [5, 8, 13, 16, 21]

    plot_fitness_history(best, average)
