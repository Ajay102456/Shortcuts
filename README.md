# Shortcuts: code, frozen protocol and results

Materials for the study *Which Signals Reveal Benchmark Shortcuts in IoT Intrusion Detection? A Frozen-Protocol Evaluation of Sufficiency, SHAP Concentration and Simple Baselines*.

The study asks whether model-based signals (sufficiency, SHAP concentration, their product, a transfer gap) detect benchmark shortcuts better than simple data-level baselines (correlation ratio, mutual information, RFE rank) on CICIoT2023, Edge-IIoTset and CICIoMT2024. Both pre-registered hypotheses were not supported; see the paper.

## Contents
| Folder | Content |
|---|---|
| `02_pipeline/` | Study decisions and research plan |
| `03_protocol/` | Pilot and full-study pre-registrations (the frozen full-study protocol is `full_study_preregistration.md`) |
| `04_code/` | `full_study.py` (experiments), `analyze_full.py` (statistics), `make_*.py` (tables and figures), `integrity_check_final.py` (asserts manuscript numbers against results), pilot code |
| `05_results/full/` | Freeze log with SHA-256 hashes, run logs, manifests, per-group score CSVs, decoy configurations, `analysis/` (exported statistics) and integrity-gate reports |
| `05_results/pilot/` | Pilot outputs |
| `tables/`, `figures/` | Manuscript tables and figures generated from the exported results |
| `refs_final.json`, `dois.txt` | Verified reference records used in the paper |

## Protocol integrity
`05_results/full/freeze_log_full.md` records the SHA-256 of the pre-registration, `full_study.py`, `analyze_full.py`, the decoy configurations and the data pools, written before any calibration or evaluation run. The three files in this repository match those hashes. The protocol was frozen locally and was not deposited in a public registry, so the hashes are the only evidence of its timing. Each evaluation seed was run once; no run failed.

## Data (not included)
The benchmarks are public and are not redistributed here: CICIoT2023 (Neto et al., Sensors 2023), Edge-IIoTset (Ferrag et al., IEEE Access 2022) and CICIoMT2024 (Dadkhah et al., Internet of Things 2024; https://www.unb.ca/cic/datasets/iomt-dataset-2024.html). The CICIoMT2024 licence is stated by the authors as CC BY-NC-ND 4.0 (non-commercial, no derivatives, attribution); please check each dataset's terms before use. The derived sample pools (`data_cache/*.npz`) are not included; the scripts rebuild them from the raw files.

## Running
The scripts use absolute paths from the original machine (`/home/s/Documents/XAI-IOTEdge/...`); edit the constants at the top of each script. Environment: Python with LightGBM 4.7.0, SHAP 0.52.0, PyTorch 2.14.1 (CPU), NumPy 2.5.3, pandas 3.0.6, scikit-learn. A full run took about 36 CPU hours.

## Licence
The repository licence is the one in `LICENSE` (CC0 1.0). It covers this code and the exported results only, not the datasets.

## AI assistance
An AI assistant (Claude, Anthropic) was used for planning, code, analysis scripting and drafting. See the paper's disclosure.

## Timestamps
`05_results/full/timestamps/` holds OpenTimestamps proofs (`.ots`) for the freeze log and the pre-registration, submitted on 2026-10-31, after the experiments. They show that these files existed by that date; they do not show that the files predate the runs. Verify with the `ots` client (`ots verify freeze_log_full.md.ots`) after the proof has been upgraded with a Bitcoin attestation.
