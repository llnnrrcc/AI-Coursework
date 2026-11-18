## Pair A - A1: Femur limits

Setup: L1 only, femur changed (`angles[1]`), coxa and tibia at 0 unless stated. Angles in radians (1 rad ≈ 57°).

**What counted as "realistic":** the knee sits above the hip (arched leg), the foot can get clearly below the body (z < 0) using a tibia angle inside A2's limits (-1.7 to 0.0), and the leg doesn't fold under the body.

**Femur elevation** (angle above horizontal) ≈ 30° + (femur angle × 57.3), because the coxa is already tilted up 30°.

### Main sweep

| Femur angle (rad) | Where does the femur point? | Looks realistic? | L1 foot z |
|---|---|---|---|
| -2.0 | Almost straight down (~85° below horizontal), knee below the body | No | -1.092 |
| -1.5 | Steeply down (~56° below), knee level with body | No | -0.808 |
| -1.0 | Angled down (~27° below), knee below hip | No, leg droops | -0.180 |
| -0.5 | Roughly flat (~1° above), knee just above hip | Yes (low, sprawled stance) | 0.640 |
| 0    | Up 30°, continues straight from coxa | No, foot can't get below the body within the tibia limits | 1.450 |
| 0.5  | Up ~59°, steep | No, foot can't reach ground | 2.052 |
| 1.0  | Nearly vertical (~87°) | No, near singularity | 2.298 |

The first pass suggested roughly -0.5 to 0.0. The edges were then narrowed below, and the upper edge was rechecked once A2's tibia limits were known.

### Narrowing down (step 6)

"Deepest foot z" is the lowest the L1 foot can get with the tibia anywhere in A2's range (-1.7 to 0.0).

| Femur angle (rad) | Where does the femur point? | Looks realistic? | L1 foot z (tibia 0) | Deepest foot z (tibia -1.7 to 0) |
|---|---|---|---|---|
| -0.6 | ~4° below horizontal, knee below hip | No | 0.470 | -0.453 |
| -0.5 | ~1° above horizontal, knee just above hip | Yes | 0.640 | -0.383 |
| -0.4 | ~7° above horizontal, clear arch | Yes | 0.810 | -0.314 |
| -0.3 | ~13° above horizontal | Yes | 0.977 | -0.240 |
| -0.2 | ~19° above horizontal | Yes (edge) | 1.141 | -0.159 |
| -0.1 | ~24° above horizontal | No, foot only 0.07 below the body | 1.299 | -0.069 |
| 0    | 30° above horizontal | No, foot can't get below the body | 1.450 | +0.027 |
| 0.1  | ~36° above horizontal | No | 1.593 | +0.129 |

### Result (step 7)

- **Femur minimum: -0.5 rad.** Below about -0.52 the femur points below horizontal, so the knee drops beneath the hip and the leg folds instead of arching.
- **Femur maximum: -0.2 rad.** Above -0.2 the femur is raised so steeply that, within the tibia limits, the foot can barely get below the body (only 0.07 at -0.1, and not at all at 0).

### Why the maximum changed from 0.0 to -0.2

The first estimate of 0.0 assumed the tibia could bend all the way to -2.0. A2's tibia limit is -1.7, and at that bend a femur of 0 leaves the foot above the body (z = +0.027). The femur and tibia limits depend on each other, so they were checked together and the femur maximum was lowered. -0.2 also matches the lower end of Wang et al.'s measured lifting angle (19°, about -0.19 rad in this model), so the final range sits where the model's geometry and the real spider data agree.

### Link to the floor

The floor is set at z = -0.30, and a foot counts as planted within 0.05 of it (z between -0.35 and -0.25). A foot more than 0.05 below the floor is penalised.

| Femur | Deepest foot z (tibia -1.7 to 0) | Can plant? |
|---|---|---|
| -0.50 | -0.383 | Yes |
| -0.40 | -0.314 | Yes |
| -0.38 | -0.300 | Yes (reaches the floor exactly) |
| -0.32 | -0.256 | Yes (just inside the band) |
| -0.30 | -0.240 | No |
| -0.20 | -0.159 | No |

So feet can be planted for femur values from -0.5 to about -0.32, roughly 60% of the femur range. The rest (about -0.32 to -0.2) is used for lifting legs during swing. Swinging the leg forward and back with the coxa does not change foot height, because the coxa rotates around the vertical axis at the hip, so a planted foot stays on the floor while the coxa moves it.

**Rejected alternative:** a floor at -0.35. It sits just above the deepest any foot can reach (-0.383), so the limits and floor agree exactly and no pose can go through the floor. But it only allows planting for femur values up to about -0.39 (about a third of the range), which pins stance poses against the femur limit and leaves the GA little room. Its below-floor penalty could also never fire.

### Standing pose (A1 and A2 together)

| Femur | Tibia | L1 foot z | Note |
|---|---|---|---|
| -0.8 | -1.2 | -0.587 | Starting pose from the plan; femur outside the agreed range |
| -0.4 | -1.2 | -0.194 | Femur moved into the middle of the planting range; foot too high |
| -0.4 | -1.4 | -0.271 | Tibia bent further; foot inside the contact band but above the floor |
| -0.4 | -1.5 | -0.295 | Chosen pose: foot 0.005 from the floor |

**Standing pose: coxa 0, femur -0.4, tibia -1.5 on all eight legs.** Every foot is at z = -0.295, almost exactly on the floor (the middle of the contact band), with reach 1.93 from the hip. Femur -0.4 sits in the middle of the planting range, so the GA can move the leg either way from this pose. Tibia -1.5 is about 86° of knee bend, close to the ~80° standing posture reported by Gartly (2023) and within the ~90° the sources call typical.

Considered: femur -0.45 with tibia -1.5 (foot z -0.338, only 0.012 from the edge of the contact band) and femur -0.45 with tibia -1.3 (foot z -0.290, a gentler 74° bend; a fine alternative).

```python
for leg in range(8):
    angles[leg * 3 + 1] = -0.4   # femur
    angles[leg * 3 + 2] = -1.5   # tibia
```

Does it look like it's standing (side view)? Yes. Every leg arches (knee above hip) and all feet sit level at the floor.
All eight feet at z = -0.295? Yes, confirmed with `spider_model.py`: every foot prints z = -0.295 and counts as planted.

> Notes:
> - Limits stay well clear of +1.05 and -2.09 rad, where the femur is vertical and the kinematics become undefined (singularity).
> - Wang et al. (2011) measured a real spider's femur lifting angle of 19–68°, which is about -0.19 to +0.65 rad in this model. The model can't use most of that range because its coxa is long (1.2) and already tilted up 30°, so a steeply raised femur lifts the foot too high to reach the ground.
> - All legs share the same hip height and segment lengths, so this range applies to all eight legs.
> - Values in the narrowing table were calculated from the leg kinematics and should be confirmed by running a few in `explore.py`.