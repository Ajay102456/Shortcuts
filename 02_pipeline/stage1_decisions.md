# Stage 1 (Research, socratic) — decision log

Paper: Explaining the Shortcut: Attribution-Based Forensics Reveal How Explainable IoT IDS Inherit Benchmark Leakage
Started: 2026-10-29. Pipeline: full, FULL checkpoints. Results policy: design protocol, run real experiments, then write; no fabricated numbers.

## Accepted decisions (user-confirmed)
- Entry: Stage 1 socratic. Seed: Shortcut_Paper/01_literature_survey/survey_report.md + Papers_md corpus.
- Shortcut definition: three-tier ladder. Tier 1 planted (certain), Tier 2 documented artifacts (Edge-IIoTset: dns.qry.name.len, mqtt.topic, mqtt.protoname, mqtt.conack.flags; plus serialisation artifact, arXiv 2608.15761), Tier 3 flagged-only (never "confirmed").
- Primary claim: A (method: SHAP-based audit vs correlation/MI/RFE on planted shortcuts), B (explanations of shortcut models look stable/plausible) as motivation, C (XAI feature selection inherits shortcut) as one demonstration.
- Core benchmarks: CICIoT2023, Edge-IIoTset (local), CICIoMT2024 (needs download). N-BaIoT optional.
- Detector design: SHAP concentration (trigger only) + group knockout with retraining + cross-benchmark transfer gap; clean control (false-alarm rate on unmodified data) and behavior-like decoy are mandatory. Signals are hypotheses; report if they fail to separate.
- Validation: calibrate on one plant family, test on a different family and on documented artifacts; transplant real artifact class-to-value structure; plant entangled and redundant shortcuts; pre-commit thresholds/plant families/metrics before touching real benchmarks.

## Failure criteria and honesty rules (user-accepted, binding)
- "Beats" = paired bootstrap 95% CI of detection-AUC difference vs correlation screen excludes 0 on the held-out plant family; minimum meaningful difference fixed before runs. If not met: report as characterization study (when correlation suffices vs not). Never change metric, drop hard plant families, or pick seeds after results.
- Clean control (unmodified data): false-alarm rate with CI is a headline result; acceptable budget fixed before runs. If exceeded: audit is a prioritization tool (precision@k), not an automatic detector. Calibrate on a calibration split; report clean-control rate on an untouched split.
- Transfer signal: report coverage of defensible CICIoT2023<->CICIoMT2024 category mappings; use only for those; ablate each signal's marginal contribution; if transfer adds nothing, claim = concentration + group knockout.
- Commitments: (1) pre-registration note with frozen thresholds/plant families/metrics/seeds/failure criteria, committed before real-benchmark runs; (2) no hand-typed numbers, script-exported tables, manifest with data hashes/seeds/versions; (3) report all runs, >=5 seeds, CIs, paired tests; (4) untouched test split, final benchmarks run once, reruns logged; (5) deviation log in paper; (6) "flagged" never "confirmed" without Tier 2 evidence, explicit limitations; (7) [RESULT] placeholders until measured, integrity gates block unprovenanced numbers; (8) verify every reference before citing (survey references.bib is incomplete); (9) disclose AI assistance, release code + manifest.

## Claim scoping, practitioner value, statistics (user-accepted)
- Claim levels: (1) benchmark permits shortcut learning [supportable]; (2) our trained models rely on flagged group [supportable]; (3) published detectors were inflated [only for pipelines we re-ran, claim C; otherwise "possible"]. Wording: flagged groups are evidence the benchmark permits shortcut learning, not that published detectors relied on them. Tier 3 flags labelled "flagged, corroborated by signals X, Y". Sharing findings/scripts with dataset maintainers before submission: courtesy, optional.
- Practitioner actions: (a) run audit on top feature groups before trusting a benchmark score; (b) report score with and without flagged groups as a range, not one corrected number; (c) require cross-benchmark test before deployment. State explicitly: an audited benchmark score does not certify deployment readiness.
- Statistics: full spread, no weighted score. Per-seed x model-family results (LightGBM, MLP, + RF for model dependence); one primary metric fixed before runs (detection AUC, seeds averaged within model family); CIs by resampling seeds and planted-shortcut instances; equal weights only if an aggregate is needed, pre-registered, with sensitivity to alternative weights; feature groups defined a priori by a fixed rule (protocol layer / feature type, or fixed-threshold correlation clustering).

## Open (to resolve before Stage 2)
- Numeric values to fix before runs: minimum meaningful AUC difference, false-alarm budget, seed count.
- Cross-benchmark label mapping CICIoT2023 <-> CICIoMT2024 (judgment call; document it).
- Download source and licence for CICIoMT2024 (UNB CIC page).

## Layer 5 (user-accepted)
- Include a "What this study does not claim" paragraph (published results not invalidated; not every flagged column is an artifact; reliance measured only on models we trained). Failure still yields reusable toolkit + characterization/negative-result paper.
- Pilot with go/no-go gate first: CICIoT2023 + LightGBM, one noisy-proxy column at 3 strengths, SHAP concentration + group knockout vs correlation screen, clean control, one behavior-like decoy. Separate calibration split and seeds; labelled pilot; pilot numbers never reused as final.
- Stage 1 deliverables compiled in stage1_research_plan.md (Devil's Advocate verdict: PASS with conditions).

## Pilot outcome (2026-10-30, run once under 03_protocol/pilot_preregistration.md)
- Pre-registered rule: GO (audit AUC >= correlation on medium and strong plants; clean FA 0.048 <= 0.05; decoy flagged 0/5). 35/35 evaluation runs ok; no deviations logged. Details: 05_results/pilot/pilot_summary.md. PILOT numbers, not final results.
- Pilot-informed observations (exploratory, to be pre-registered before the full study): (1) sufficiency (single-group retraining) did most of the detecting; SHAP concentration alone was weaker and diluted under redundancy (redundant_ungrouped: audit AUC 0.892 < correlation 0.909, TPR 0). (2) 'Tot sum' was flagged in 4 of 5 clean runs (Tier 3, unconfirmed). (3) GO rule is weak: ties pass, FA threshold is 5% by construction.
