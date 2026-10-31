| Item | Value |
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
