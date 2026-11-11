
import numpy as np
from chromosome import N_GENES, LOW, HIGH
from operators import crossover, mutate

LOW = np.asarray(LOW)
HIGH = np.asarray(HIGH)

# Make two random valid chromosomes
p1 = np.random.uniform(LOW, HIGH)
p2 = np.random.uniform(LOW, HIGH)

# Test crossover
child1, child2 = crossover(p1, p2)

for leg in range(4):
    start = leg * 9
    end = start + 9

    block1 = child1[start:end]
    block2 = child2[start:end]

    # Every child gets a complete leg from one parent
    assert np.array_equal(block1, p1[start:end]) or \
           np.array_equal(block1, p2[start:end])

    # Children should receive opposite parent blocks
    assert np.array_equal(block1, p1[start:end]) == \
           np.array_equal(block2, p2[start:end])

# Ensure crossover did not modify the parents
assert np.all(p1 >= LOW) and np.all(p1 <= HIGH)
assert np.all(p2 >= LOW) and np.all(p2 <= HIGH)

# Test mutation 1,000 times
current = p1.copy()

for _ in range(1000):
    current = mutate(current, 0.1)

    assert current.shape == (N_GENES,)
    assert np.all(current >= LOW - 1e-12)
    assert np.all(current <= HIGH + 1e-12)

print("All operator tests passed!")
