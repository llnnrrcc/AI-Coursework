## Pair A - A1: Femur limits

| Femur angle (rad) | Where does the femur point? | Looks realistic? | L1 foot z |
|---|---|---|---|
| -2.0 | Almost straight down (~85° below horizontal), knee below the body | No | -1.092 |
| -1.5 | Steeply down (~56° below), knee level with body | No | -0.808 |
| -1.0 | Angled down (~27° below) | Borderline, leg droops | -0.180 |
| -0.5 | Roughly flat, out sideways | Yes (low, sprawled stance) | 0.640 |
| 0    | Up 30°, continues straight from coxa | Yes | 1.450 |
| 0.5  | Up ~59°, steep | No, foot can't reach ground | 2.052 |
| 1.0  | Nearly vertical (~87°) | No, near singularity | 2.298 |

based on this I'd suggest a range between -0.5 and 0.5

### Narrowing down (step 6)

| Femur angle (rad) | Where does the femur point? | Looks realistic? | L1 foot z |
|-------------------|-----------------------------|------------------|-----------|
| -0.6              | ~4° below horizontal, knee below hip | No | 0.470 |
| -0.5              | ~1° above horizontal, knee just above hip | Yes | 0.640 |
| -0.4              | ~7° above horizontal, clear arch | Yes | 0.810 |
| -0.1              | ~24° above horizontal | Yes | 1.299 |
| 0                 | 30° above horizontal; foot only just reaches z < 0 with tibia fully bent | Yes (edge) | 1.450 |
| 0.1               | ~36° above horizontal; foot can't get below body | No | 1.593 |

### Result (step 7)

- **Femur minimum: -0.5 rad.** Below about -0.52 the femur points below horizontal, so the knee drops beneath the hip and the leg folds instead of arching.
- **Femur maximum: 0.0 rad.** Above 0 the femur is raised so steeply that the foot cannot reach below the body, even with the tibia fully bent.

> Notes:
> - Elevation of the femur ≈ 30° + (femur angle × 57.3), since the coxa is already tilted up 30°.
> - Limits stay well clear of +1.05 and -2.09 rad, where the femur is vertical and the kinematics become undefined (singularity).
> - Wang et al. (2011) measured a real spider's femur lifting angle of 19–68°, which is about -0.2 to +0.65 rad in this model. The overlap with the model's usable range is -0.2 to 0.0, which could be used as a tighter "most realistic" range.