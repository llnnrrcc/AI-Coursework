
import numpy as np
from chromosome import N_GENES, LOW, HIGH
from operators import crossover, mutate

LOW = np.asarray(LOW)
HIGH = np.asarray(HIGH)

# Make two random valid chromosomes
p1 = np.random.uniform(LOW, HIGH)
p2 = np.random.uniform(LOW, HIGH)

# Save copies of the parents before crossover
p1_original = p1.copy()
p2_original = p2.copy()

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

# Check that crossover did not modify either parent
assert np.array_equal(p1, p1_original)
assert np.array_equal(p2, p2_original)

# Test mutation 1,000 times
current = p1.copy()

for _ in range(1000):
    current = mutate(current, 0.1)

    assert current.shape == (N_GENES,)
    assert np.all(current >= LOW - 1e-12)
    assert np.all(current <= HIGH + 1e-12)


# Test that crossover gives the same results with the same seed
rng1 = np.random.default_rng(42)
rng2 = np.random.default_rng(42)

child_a1, child_a2 = crossover(p1, p2, rng1)
child_b1, child_b2 = crossover(p1, p2, rng2)

assert np.array_equal(child_a1, child_b1)
assert np.array_equal(child_a2, child_b2)

# Test that mutation gives the same results with the same seed
rng3 = np.random.default_rng(42)
rng4 = np.random.default_rng(42)

mutated_a = mutate(p1, 0.1, rng3)
mutated_b = mutate(p1, 0.1, rng4)

assert np.array_equal(mutated_a, mutated_b)

# Check that mutation did not modify the original parent
assert np.array_equal(p1, p1_original)

print("Seeded randomness tests passed!")
print("All operator tests passed!")
