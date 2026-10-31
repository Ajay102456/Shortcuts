# Full-study pre-registration — DRAFT v1 (NOT FROZEN; awaiting author review)

Paper: Explaining the Shortcut (working title; see section 9)
Status: DRAFT. Nothing in the full study has been run. This note is pilot-informed: the changes from the original design were chosen after seeing pilot results (05_results/pilot/pilot_summary.md), so they are exploratory and are declared as such. It becomes binding only when the author approves it and its sha256 is recorded in 05_results/freeze_log_full.md before any full-study run.

## 1. What the pilot changed
- Sufficiency (retrain on one feature group only) did most of the detecting; SHAP concentration alone was weaker and was diluted when a shortcut was spread over several differently encoded columns (pilot: audit AUC 0.892 vs correlation 0.909, TPR 0).
- `Tot sum` was flagged in 4 of 5 clean pilot runs (unconfirmed).
- The pilot go rule was weak (ties pass, easy plants, decoy of low SHAP mass).
Consequence: sufficiency is the primary signal; SHAP concentration, necessity and cross-benchmark transfer are reported as separately evaluated components. No weighted combination. The product score from the pilot stays as one reported variant.

## 2. Author-fixed values (carried over from Stage 1)
False-alarm budget 5% of groups. Minimum AUC advantage 0.05, with a paired-bootstrap 95% CI excluding 0. Failure criteria and honesty commitments as in 02_pipeline/stage1_decisions.md. New for the full study: **30 seeds** per condition (author approved "30+" on 2026-10-30).

## 3. Design factors
- **Benchmarks:** CICIoT2023 (8-class grouping, existing loader), Edge-IIoTset (ML-ready CSV, string columns encoded per section 7), CICIoMT2024 (to be downloaded; licence to check; category mapping documented). N-BaIoT dropped from the core study (author scope decision: 3 benchmarks).
- **Model families:** LightGBM, compact MLP (src/models.py), random forest. Each reported separately; no pooling across families.
- **Seeds:** calibration seeds 1001-1030 (clean runs and plant-family A), evaluation seeds 2001-2030. Evaluation seeds untouched until this note and the code are hashed.

## 4. Plant families
- **Family A (calibration):** noisy proxy, rho in {0.6, 0.8, 0.95}; exact label copy.
- **Family B (held-out; thresholds are never fitted on it):**
  - redundant-grouped and redundant-ungrouped (k=5, rho=0.8), as in the pilot;
  - entangled: plant = class map value + beta x a real feature (beta in {0.5, 1.0}), so it correlates with real traffic;
  - transplanted: the empirical class-to-value structure of the four documented Edge-IIoTset artifacts (`dns.qry.name.len`, `mqtt.conack.flags`, `mqtt.protoname`, `mqtt.topic`) copied onto CICIoT2023 classes by a fixed class mapping.
- **Tier 2 real check:** the four documented columns inside the real Edge-IIoTset file (no planting).

## 5. Controls
- **Clean control:** unmodified data; false-alarm rate with CI on the evaluation seeds; thresholds from calibration seeds only.
- **Hard decoys (new):** (a) a derived column with strong genuine class signal (the highest-eta real-feature ratio chosen by a fixed rule on the calibration seeds); (b) two decoys with SHAP mass at the 75th and 90th percentile of real groups (selected on calibration seeds). The pilot decoy was too easy.
- **Natural-feature report:** every group flagged on clean data (e.g. `Tot sum`) is listed as Tier 3 "flagged, unconfirmed" and checked with necessity and transfer before any wording stronger than that is used.

## 6. Signals and variants (all reported separately)
Sufficiency S_g (primary); concentration C_g; necessity R_g (retrain without g, computed for all groups); transfer gap T_g (CICIoT2023 <-> CICIoMT2024 on mapped categories only; coverage reported); pilot product A_g = C_g x S_g. Groups by the pilot rule (|Pearson| average linkage, cut 0.10). Extra grouping variant for ablation only: clustering on the correlation ratio, to test whether differently encoded redundant copies are merged.
Baselines: correlation ratio eta, mutual information, RFE rank, adversarial validation (as in the Edge-IIoTset leakage study).

## 7. Encoding rule (Edge-IIoTset strings)
Target-agnostic ordinal encoding by sorted unique value, fitted on the training split. No target encoding.

## 8. Metrics and tests
- Primary metric: group-level detection AUC, averaged over seeds within each model family and benchmark.
- Primary comparisons (pre-specified): primary signal vs the best baseline, on Family B, for each of 3 model families x 3 benchmarks = 9 comparisons. Paired bootstrap over seeds and plant instances; Holm correction across the 9. "Beats" = difference >= 0.05 and the corrected CI excludes 0.
- Secondary: TPR at the 5% FA threshold, precision@k, FA on clean and decoys with CIs, ablation of each signal, Tier 2 recovery rate.
- Full spread is shown; no weighted aggregate.

## 9. Claim and title consequence (to be decided from results, not now)
If sufficiency is the main winner and SHAP adds nothing significant, the paper will not be titled or framed as "attribution-based". Candidate reframing: a sufficiency-and-attribution audit, or a characterization of when each signal works. The decision rule: SHAP concentration earns the title claim only if its added AUC over sufficiency alone is >= 0.05 with a corrected CI excluding 0 on at least one held-out family; otherwise it is reported as an ablation.

## 10. Compute estimate (rough, unverified until run)
About 16 s per LightGBM run in the pilot. Rough budget: LightGBM roughly 1-2 h, random forest similar, MLP and the all-groups necessity runs several times more. To be measured on a 1-seed timing run before freezing; the budget will be written into the freeze log.

## 11. Conduct
Same rules as the pilot: freeze hash before code, code hash before evaluation seeds, smoke tests on non-evaluation seeds with output discarded, evaluation seeds run once, all runs logged, deviation log, script-exported numbers only, released manifest.

## 12. Open decisions for the author before freezing
1. Approve or edit sections 3-8.
2. Download CICIoMT2024 and confirm its licence and category mapping.
3. Confirm dropping N-BaIoT.
4. Confirm the hard-decoy rule (section 5).
5. Approve the timing run and compute budget (section 10).

## 13. CICIoMT2024 facts and proposed handling (added 2026-10-30 after inspecting the local files; no results involved)
- Local path: Journal MDPI sensors/data/raw/ciciomt2024/{train,test}/*.pcap.csv (train 1.8 GB, test 394 MB; the rest of the 92 GB folder is pcaps and archives and is not used). 45 feature columns, no label column; label = file name (same convention as CICIoT2023).
- Licence: the README does not state terms; to be confirmed with the dataset page. Required citation: Dadkhah et al., CICIoMT2024, Internet of Things, vol. 28, Dec 2024.
- Feature overlap with the CICIoT2023 pool: 38 shared features. CICIoT2023 pool only: `Time_To_Live`. CICIoMT2024 only: `Duration`, `Srate`, `Drate`, `Magnitue`, `Radius`, `Covariance`, `Weight`. `Time_To_Live` vs `Duration` may be the same underlying column under different names; unverified, so transfer uses the 38 shared features only.
- Category mapping (judgment, documented): Benign->Benign; ARP_Spoofing->Spoofing; Recon-*->Recon; TCP_IP-DDoS-*->DDoS; TCP_IP-DoS-*->DoS. The five MQTT-* files have no CICIoT2023 counterpart and are excluded from transfer. Coverage: 5 of 8 CICIoT2023 classes (Mirai, Web, BruteForce unmapped).
- Row counts (train / test): Benign 192,732 / 37,607; Spoofing 16,047 / 1,744; Recon 103,726 / 27,676; DDoS 4,779,859 / 1,066,764; DoS 1,805,529 / 416,676; MQTT (unmapped) 262,938 / 63,715. Heavily imbalanced; per-seed sampling must be stratified by mapped class with a cap (proposed 1,500 per class, 1,000 for Spoofing test side subject to availability).
- CICIoMT2024 as a third benchmark for sufficiency/concentration: classes = its 5 mapped categories plus MQTT (6 classes), same pipeline as the other benchmarks.

## 14. Compute-driven changes and code-forced decisions (added 2026-10-30; supersede conflicting text in sections 3, 6, 10)
Timing (v1, all-groups necessity, seconds per run): CICIoT2023 LightGBM 54, RF 36, MLP 95; Edge-IIoTset LightGBM 65; CICIoMT2024 LightGBM 42 (timing_v1_all_groups/). Full original design extrapolated to roughly 4 days; author chose cuts below on 2026-10-30.
- **Calibration seeds:** 1001-1010 (10), not 30. Evaluation seeds: 2001-2030 for LightGBM and RF; 2001-2015 (15) for the MLP.
- **Necessity R_g** is computed only for the top-10 groups ranked by sufficiency S_g (rank-based, no threshold). Groups outside the top 10 have no R_g; R_g is not used in any primary comparison.
- **Transfer T_g:** trained on group g alone over the mapped categories (Benign, DDoS, DoS, Recon, Spoofing); T_g = in-domain macro-F1 minus cross-domain macro-F1. Shared-feature groups only (38 shared features). Per-domain z-scoring (removes absolute scale shifts; limitation). Planted columns in the other domain are random permutations of the source column (no label relation there); decoys are recomputed from the other domain's real features. Limitation to state: this makes transfer detect planted shortcuts by construction, so the transfer signal is judged mainly on the real Edge-IIoTset artifacts and the clean-control false alarms, not on planted AUC alone.
- **Edge-IIoTset base features:** drop the 13 identifier/payload fields used in the Edge-IIoTset leakage study plus Attack_label; keep other strings, ordinal-encoded on the training split; the four documented artifacts are removed from the clean base and present only in condition `tier2_real`. 800 rows per class.
- **MLP explainer:** SHAP GradientExplainer, 100 background rows, 200 explained rows (RF: 300 explained rows; LightGBM: 1000).
- **Adversarial validation:** dataset-level diagnostic only (one train-vs-test AUC), not a group-level baseline. Group-level baselines: correlation ratio, mutual information, RFE rank.
- **Class mapping for transplanted artifacts (CICIoT2023 -> Edge-IIoTset class):** Benign->Normal, BruteForce->Password, DDoS->DDoS_TCP, DoS->DDoS_HTTP, Mirai->DDoS_UDP, Recon->Port_Scanning, Spoofing->MITM, Web->SQL_injection. Judgment table; Mirai has no real counterpart.
- **CICIoMT2024 as a benchmark:** 6 classes (5 mapped + MQTT), 1,500 per class cap, all 45 features, head-of-file sampling (6,000 rows per file, same limitation as CICIoT2023). Transplanted condition is skipped for CICIoMT2024 and Edge-IIoTset.
- **Decoys:** pairs chosen on calibration seed 1001 (decoy_config_*.json). Edge-IIoTset pairs include identifier-like fields (e.g. icmp.seq_le, dns.qry.name); author to confirm or replace.
- **Pilot-informed status:** all of section 14 is exploratory; none of it was tuned on evaluation-seed data (no evaluation seed has been run).
