T={}
T["t_datasets"]="""| Benchmark | Classes | Rows per class per seed | Rows per seed | Features in models | Source |
|---|---|---|---|---|---|
| CICIoT2023 | 8 | 1,500 | 12,000 | 39 | Project pool of 31,998 rows (head-of-file) |
| Edge-IIoTset | 15 | 800 | 12,000 | 44 (clean base) | ML-ready file, 157,800 rows before duplicate removal |
| CICIoMT2024 | 6 | 1,500 | 9,000 | 45 | Train-side pool of 24,000 rows, and a test-side pool of 21,744 rows used for transfer |
"""
T["t_conditions"]="""| Condition | Family | Construction | Benchmarks |
|---|---|---|---|
| clean | control | No modification | all |
| decoy_a, decoy_b75, decoy_b90 | control | Product of two standardised real features (highest eta, or SHAP mass at the 75th or 90th percentile) | all |
| exact_copy | A | Class-wise random value, agreement 1.0 | all |
| plant_weak, plant_medium, plant_strong | A | Class-wise random value, agreement 0.6, 0.8, 0.95 | all |
| redundant_grouped | B | Five scaled and shifted copies of one agreement-0.8 plant (clusters into one group) | all |
| redundant_ungrouped | B | Five independent agreement-0.8 plants (separate groups) | all |
| entangled_0.5, entangled_1.0 | B | Agreement-0.8 plant plus beta times a standardised real feature (beta 0.5 or 1.0) | all |
| transplanted | B | Class-to-value distribution of the four Edge-IIoTset artifact columns copied onto CICIoT2023 classes | CICIoT2023 |
| tier2_real | Tier 2 | Real Edge-IIoTset file with the four documented artifact columns, with nothing planted | Edge-IIoTset |
"""
T["t_signals"]="""| Signal | Symbol | Definition | Uses a trained model | Evaluated on |
|---|---|---|---|---|
| Sufficiency | S | Macro-F1 of a model trained on the group alone, divided by the full model's | yes | all groups |
| SHAP concentration | C | Group share of total mean absolute SHAP | yes | all groups |
| Audit score | A | C times S | yes | all groups |
| Necessity | R | Macro-F1 without the group, divided by the full model's | yes | top-10 groups by S |
| Transfer gap | T | In-domain minus cross-domain macro-F1 (CICIoT2023 and CICIoMT2024, five shared classes) | yes | CICIoT2023, CICIoMT2024 |
| Correlation ratio | eta | Square root of between-class over total variance | no | all groups |
| Mutual information | MI | Mutual information between feature and label | no | all groups |
| RFE rank | RFE | Rank in recursive feature elimination | wrapper | all groups |
"""
T["t_protocol"]="""| Item | Value |
|---|---|
| Pilot | CICIoT2023, LightGBM, seeds 101-105 (separate pre-registration) |
| Calibration seeds | 1001-1010 (clean, Family A, decoys) |
| Evaluation seeds | 2001-2030 for LightGBM and random forest and 2001-2015 for the neural network, each run once |
| Threshold | 95th percentile of clean calibration groups, per benchmark, model and signal |
| Primary metric | Group-level detection AUC, Family B mean per seed |
| Tests | Paired bootstrap over seeds (10,000 resamples), Holm over nine combinations |
| Decision rule | Difference at least 0.05 and Holm p below 0.05 |
| Freeze | Pre-registration, code, decoy configs and data pools hashed (SHA-256) before any calibration or evaluation run |
| Failures | No run failed, no run was repeated, and no deviation was recorded |
| Compute | CPU only, with about 36 hours estimated for the full run |
"""
T["t_procedure"]="""| Step | Action | Evidence in this study |
|---|---|---|
| 1 | Compute class-dependence statistics per feature group (correlation ratio and mutual information) on the training split and flag groups above a threshold set on clean groups | The correlation ratio flagged all four documented Edge-IIoTset artifact groups, and mutual information was the strongest baseline on planted shortcuts |
| 2 | Inspect each flagged group: does the field identify the capture process, the tool or the protocol implementation rather than attack behaviour? | The four documented fields are protocol-identity columns |
| 3 | Run a hard-decoy control: add informative columns that are not shortcuts and check that they are not flagged at the same threshold | Sufficiency flagged the 90th-percentile decoy in 3 of 27 cells, and the transfer gap flagged decoys in 9 of 18 cells |
| 4 | Optionally add a model-based score (sufficiency) as a second view, and treat its flags as unconfirmed | Sufficiency flags natural features on clean data (for example Tot sum) and missed the documented artifacts |
| 5 | Do not use the transfer gap as confirmation, and report ceiling effects where scores saturate | Edge-IIoTset scores reached 0.998 to 1.000 for several signals |
| 6 | Set thresholds on separate seeds, report the clean false-alarm rate, and fix the protocol before the evaluation runs | The 5% budget was met only approximately (28 of 60 cells above 0.05) |
"""
import sys
for k,v in T.items(): open(f"/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/06_manuscript/tables/{k}.pipe.md","w").write(v)
