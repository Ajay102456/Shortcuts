| Condition | Family | Construction | Benchmarks |
|---|---|---|---|
| clean | control | No modification | all |
| decoy_a, decoy_b75, decoy_b90 | control | Product of two standardised real features (highest eta; SHAP mass at 75th and 90th percentile) | all |
| exact_copy | A | Class-wise random value, agreement 1.0 | all |
| plant_weak, plant_medium, plant_strong | A | Class-wise random value, agreement 0.6, 0.8, 0.95 | all |
| redundant_grouped | B | Five scaled and shifted copies of one agreement-0.8 plant (clusters into one group) | all |
| redundant_ungrouped | B | Five independent agreement-0.8 plants (separate groups) | all |
| entangled_0.5, entangled_1.0 | B | Agreement-0.8 plant plus beta times a standardised real feature (beta 0.5 or 1.0) | all |
| transplanted | B | Class-to-value distribution of the four Edge-IIoTset artifact columns copied onto CICIoT2023 classes | CICIoT2023 |
| tier2_real | Tier 2 | Real Edge-IIoTset file with the four documented artifact columns; nothing planted | Edge-IIoTset |
