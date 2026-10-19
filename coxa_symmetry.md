
# B-B2: Coxa Symmetry Findings

## 1. Symmetry Testing

I tested the front-left (L1) and front-right (R1) legs using the same femur angle (-0.8 radians) and tibia angle (-1.2 radians).

When the coxa angles were opposite (L1 = 0.4, R1 = -0.4), both feet had matching X and Z coordinates and opposite Y coordinates. This confirmed a mirrored pose.

When both coxa angles were set to 0.4 radians, the foot positions were no longer mirrored.

**Conclusion:** The right coxa angle must have the opposite sign to the left coxa angle to produce mirrored leg positions. The femur and tibia angles can remain the same.

## 2. Coxa Symmetry Test Results

| Test | L1 coxa (rad) | R1 coxa (rad) | L1 foot (X, Y, Z) | R1 foot (X, Y, Z) | Mirrored? |
|---|---|---|---|---|---|
| Same signs | 0.4 | 0.4 | (1.740, 2.381, -0.587) | (2.735, -1.386, -0.587) | No |
| Opposite signs | 0.4 | -0.4 | (1.740, 2.381, -0.587) | (1.740, -2.381, -0.587) | Yes |

## 3. Left-Right Leg Symmetry and Chromosome Indices

| Mirror pair | Left coxa | Right coxa | Left femur | Right femur | Left tibia | Right tibia |
|---|---|---|---|---|---|---|
| L1 / R1 | 0 | 21 | 1 | 22 | 2 | 23 |
| L2 / R2 | 3 | 18 | 4 | 19 | 5 | 20 |
| L3 / R3 | 6 | 15 | 7 | 16 | 8 | 17 |
| L4 / R4 | 9 | 12 | 10 | 13 | 11 | 14 |

**Symmetry rule:** For corresponding left-right legs, the coxa angles should have opposite signs, while the femur and tibia angles can use matching values to produce mirrored poses.

## 4. Chromosome Design: B-B2 Research

| Question | Option | Advantages | Disadvantages | Suggested approach |
|---|---|---|---|---|
| Joint limits | Clip angles after generation | Simple to implement and keeps resulting angles within limits | Can produce repeated boundary values and reduce variation | Consider as an alternative |
| Joint limits | Encode genes within valid ranges | Prevents invalid angles when properly implemented | Requires bounded mutation and suitable encoding | Preferred option |
| Crossover | Unrestricted crossover | Allows more combinations of genes | May disrupt useful combinations of joint parameters | Consider as comparison |
| Crossover | Whole-leg crossover | Preserves combinations of parameters controlling each leg | Can restrict combinations between individual joints | Preferred starting option |
| Gene organisation | Group genes by leg | Makes it easier to exchange complete leg-control patterns | Less flexibility if only whole-leg exchanges are permitted | Recommended starting point |

These chromosome design approaches are recommendations for group discussion, not final agreed decisions.
