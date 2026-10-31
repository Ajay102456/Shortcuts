# Pilot pre-registration — frozen before any detector code or evaluation-seed run

Paper: Explaining the Shortcut (see 02_pipeline/stage1_research_plan.md)
Status: PILOT. Its purpose is a go/no-go decision. Pilot numbers are never reused as final results and are labelled "pilot" wherever they appear.

## 1. Author-fixed thresholds (user-confirmed 2026-10-30)
- False-alarm (FA) budget on the clean control: **5%** of groups.
- Minimum AUC advantage over the correlation screen that counts as "beats" (full study; the CI must also exclude 0): **0.05**.
- Seeds: **5** per condition. Calibration seeds {101,102,103,104,105}; evaluation seeds {201,202,203,204,205}. The evaluation seeds are not touched until this file and the code are hashed.
- Pilot go/no-go rule: **GO iff** (i) mean group-level detection AUC of the audit >= that of the correlation screen on BOTH the medium (rho=0.8) and strong (rho=0.95) noisy-proxy plants; AND (ii) clean-control FA <= 5% on the evaluation seeds; AND (iii) the decoy is flagged in 0 of 5 evaluation seeds. Otherwise NO-GO: redesign, or take the characterization-paper route. Point estimates only (5 seeds are too few for meaningful CIs; intervals are shown descriptively).
- Known weakness of this rule, accepted in advance: ties pass condition (i). Where both detectors reach ~1.0 on easy plants, the pilot cannot separate them; the redundant conditions and the decoy are the informative ones.

## 2. Data
- CICIoT2023 via the existing loader (`src/data.py`, `load_ciciot2023`, 8-class grouping, n_per_class=4000, random_state=0). 31,998 rows x 39 numeric features, 8 classes. Pool sha256: 04cbc572d8c3dabc2a5d893a9c50f1a2a3d3b08f592b98a3cb039be166e4f83e.
- Per seed: stratified subsample of 1,500 rows per class from the pool, then a stratified 75/25 train/test split, all keyed to the seed.
- Limitation: the loader reads the head of each raw CSV, so the pool is not a uniform sample of the corpus. Seeds vary the subsample, split and model seed, but not the underlying pool. CICIoT2023 has no session identifiers.

## 3. Model
LightGBM as in `src/models.py::train_lightgbm` (150 trees, num_leaves 31, max_depth 6, learning_rate 0.1, multiclass), random_state = seed. No tuning.

## 4. Conditions (each run on every seed)
1. **clean**: unmodified 39 features.
2. **decoy**: adds one behavior-like column = `Max - Min` (a legitimate derived feature of real traffic; uses no label information).
3. **plant_weak / plant_medium / plant_strong**: adds one noisy-proxy column. Per row, with probability rho in {0.6, 0.8, 0.95} the value is m[y], otherwise m[y'] for y' drawn uniformly from the other classes. m is a fixed random draw from N(0,1) per class per seed.
4. **redundant_grouped**: adds 5 columns, rho=0.8, sharing ONE flip mask and ONE class map, each a distinct linear rescaling (scale a_j, offset b_j) of the same base column.
5. **redundant_ungrouped**: adds 5 columns, rho=0.8, sharing ONE flip mask but with a DIFFERENT random class map per column (non-linearly related).
Plants are applied before the split, as a function of the true label.

## 5. Groups (a-priori rule)
Hierarchical clustering on the training features (including any added columns), distance = 1 - |Pearson r|, average linkage, cut at distance 0.10. Each cluster is one group.

## 6. Signals and scores
- **C_g (concentration)**: TreeSHAP on a random 1,000-row test subset; mean |SHAP| over rows and classes; group value = sum over members divided by the total over all features.
- **Suff_g (sufficiency knockout)**: macro-F1 on the test set of a LightGBM trained ONLY on group g's columns, divided by the full-model macro-F1.
- **Resil_g (necessity knockout)**: macro-F1 of a model trained WITHOUT group g divided by the full-model macro-F1; computed only for the top-5 groups by A_g; descriptive, not part of any AUC.
- **Audit score A_g = C_g x Suff_g** (no weights). Ablations reported separately: C_g alone, Suff_g alone.
- **Correlation baseline**: group score = max over members of the correlation ratio eta (feature vs class label), computed on the training split.
- Cross-benchmark transfer is NOT part of the pilot.

## 7. Metrics
- Per run: group-level detection AUC (positives = groups containing a planted column; negatives = all other groups) for A_g, C_g, Suff_g and the baseline.
- FA threshold: the 95th percentile of A_g (and of the baseline score) over all groups pooled across the five clean calibration-seed runs. Applied unchanged to evaluation seeds.
- Clean-control FA = fraction of groups with A_g above the threshold in the clean evaluation runs (pooled and per seed). Groups flagged in clean runs are listed for inspection as Tier 3 "flagged, unconfirmed"; CICIoT2023 may contain natural shortcuts, so clean-run flags are not necessarily false alarms. They are counted as false alarms here, which is conservative for the audit.
- TPR at the FA threshold for each plant condition.
- Decoy flagged: decoy group's A_g above the threshold.

## 8. Added or changed relative to the accepted Stage 1 pilot (disclosed deviations)
- "Group knockout with retraining" is operationalized as sufficiency (train only on g) and necessity (train without g). Reason: in a feature-rich dataset removing one group is expected to be compensated by correlated features, so necessity alone may not discriminate; sufficiency is cheap and testable. Both are reported.
- Two redundant-plant conditions added to test the "SHAP dilution under redundancy" risk (Devil's Advocate item 1). The pilot spec said one noisy-proxy column at three strengths.
- Decoy defined as Max - Min.

## 9. Conduct rules
- Order: freeze this file (sha256 recorded) -> write code -> smoke test on a non-evaluation seed (seed 1, reduced size, output discarded) -> record code sha256 -> run calibration seeds -> run evaluation seeds once.
- Every run is logged, including failures. Reruns only after a crash, and logged. Any change after the hash is entered in the deviation log (05_results/pilot/deviation_log.md).
- All reported numbers come from script-exported CSV files; none are typed by hand.
- Pilot outputs are labelled PILOT and are not final results.
