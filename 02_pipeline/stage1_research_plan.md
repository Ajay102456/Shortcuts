# Stage 1 deliverables — Research Plan Summary, RQ Brief, Methodology Blueprint

Paper: *Explaining the Shortcut: Attribution-Based Forensics Reveal How Explainable IoT IDS Inherit Benchmark Leakage*
Status: DRAFT for the Stage 1 checkpoint. Contains no experimental results. Every numeric threshold is intentionally left for the author to fix before any run.
Decisions source: stage1_decisions.md (all items user-accepted). Sections marked [AI-PROPOSED] were AI-generated at the user's request and accepted.

---

## 1. Research Plan Summary (what the author decided)

- **Core idea:** detect benchmark shortcuts in IoT/IIoT intrusion-detection data from model attributions, without capture-session identifiers, and show that explainable IDS pipelines can inherit those shortcuts.
- **Shortcut definition:** three-tier evidence ladder. Tier 1 planted (certain); Tier 2 documented artifacts (Edge-IIoTset: `dns.qry.name.len`, `mqtt.topic`, `mqtt.protoname`, `mqtt.conack.flags`; serialisation artifact, arXiv 2608.15761); Tier 3 flagged-only, never called "confirmed".
- **Primary claim A (method)**, supported by B (explanations of shortcut-reliant models look stable/plausible) and C (SHAP-top-k feature selection inherits the shortcut).
- **Core benchmarks:** CICIoT2023, Edge-IIoTset (local), CICIoMT2024 (download needed). N-BaIoT optional.
- **Detector design:** SHAP concentration as trigger only; group knockout with retraining; cross-benchmark transfer gap. Mandatory clean control and behavior-like decoy.
- **Honesty rules:** failure criteria, nine commitments, three-level claim scoping and "does not claim" paragraph (see stage1_decisions.md).
- **Process:** pilot with go/no-go gate on CICIoT2023 + LightGBM before the full study.

## 2. Research Question Brief

**Primary RQ.** Can an attribution-based audit (SHAP concentration, group knockout with retraining, cross-benchmark transfer gap) detect benchmark shortcuts in IoT/IIoT intrusion-detection datasets without capture-session identifiers, and does it do so better than correlation, mutual-information and RFE screening?

**Sub-questions**
- **RQ1 (claim A).** At a pre-set false-alarm budget, how well does the audit detect shortcuts from a held-out planted family and the documented Tier 2 artifacts, compared with the baselines?
- **RQ2 (ablation).** What does each of the three signals contribute on its own and in combination?
- **RQ3 (claim B).** Do SHAP explanations of shortcut-reliant models remain as stable across seeds as those of clean models, and is attribution mass on shortcut features concentrated enough to look plausible to an analyst? [Operationalization of "plausible" is an open item.]
- **RQ4 (claim C).** Does SHAP-top-k feature selection run on contaminated data retain the shortcut, as measured by knockout and cross-benchmark transfer?

**FINER (qualitative, no scores):** Feasible: high for local data, medium for the CICIoMT2024 download. Interesting: high for IDS evaluation practice. Novel: medium (two 2026 leakage papers exist; novelty is explanation-based detection, no session IDs, planted-ground-truth validation, multi-benchmark scope). Ethical: no human subjects; public datasets, licences to check. Relevant: high.

**Scope.** In: tabular flow/packet-feature IDS benchmarks; tree and MLP models; SHAP. Out: raw-packet deep models, live deployment, human studies, certifying any benchmark as clean, claims about specific published papers.

## 3. Methodology Blueprint [AI-PROPOSED, accepted in parts]

**Paradigm / design:** positivist, quantitative, controlled experimental benchmark study with planted ground truth.

**Phases**
0. **Pilot (go/no-go).** CICIoT2023, LightGBM, one noisy-proxy column at three strengths; SHAP concentration + group knockout vs correlation screen; clean control; one behavior-like decoy. Separate calibration split and seeds. Label as pilot; pilot numbers are never reused as final results. Go/no-go criteria are fixed by the author beforehand.
1. **Protocol freeze.** Pre-registration note: thresholds, plant families, metrics, seeds, failure criteria, feature-group rule, committed (git hash) before real-benchmark runs.
2. **Planted shortcuts.** Families: exact label copy; noisy proxy; protocol-identity-style categorical; redundant multi-column encoding; entangled (partly predictable from real features); transplanted real-artifact structure (class-to-value relation copied from Edge-IIoTset artifacts). Calibrate on one family, evaluate on another. Strength grid set in the pre-registration.
3. **Audit signals.** (a) group-level SHAP concentration per class; (b) group knockout with retraining, curve shape; (c) cross-benchmark transfer gap on defensible CICIoT2023 <-> CICIoMT2024 category mappings (coverage reported).
4. **Baselines.** Univariate correlation screen, mutual information, RFE, adversarial validation (as in the Edge-IIoTset leakage study).
5. **Models/explainers.** LightGBM, MLP (existing code), RF for model dependence. TreeSHAP for trees; the MLP explainer is a design decision (see open items).
6. **Metrics.** Primary: detection AUC, seeds averaged within model family. Secondary: TPR at the pre-set false-alarm budget, precision@k, false-alarm rate on clean control with CI. No weighted aggregate score.
7. **Statistics.** Per-seed x model-family results reported in full; CIs by resampling seeds and plant instances; paired bootstrap for the A-vs-baseline comparison.
8. **Claims B and C experiments.** B: explanation stability (e.g. top-k overlap across seeds) on clean vs contaminated models. C: replicate a SHAP-top-k selection pipeline on contaminated vs clean data; test with knockout and transfer.
9. **Cross-benchmark study.** CICIoT2023, Edge-IIoTset, CICIoMT2024; Tier 3 flags reported as "flagged, corroborated by signals X, Y".
10. **Reproducibility.** Manifest with dataset file hashes, seeds, library versions; script-exported tables; deviation log; released code.

**Validity threats to address in the paper:** planted != real; dataset-specific; no session IDs; label-mapping judgement; SHAP instability with correlated features; model-family dependence; pilot-to-final leakage.

## 4. Devil's Advocate checkpoint (Phase 1)

| # | Issue | Severity | Required action |
|---|---|---|---|
| 1 | **SHAP dilution under redundancy.** A shortcut encoded redundantly across many columns spreads attribution, lowering per-feature concentration, which is the very case the correlation paper found. Concentration may miss it. | Major | Use group-level SHAP with a-priori groups; test explicitly in the pilot and in the redundant plant family; report if it fails. |
| 2 | **Circular validation.** Detector evaluated on shortcuts the author designed. | Major | Held-out plant family + documented artifacts + transplanted structure; calibrate/evaluate split already accepted. |
| 3 | **Novelty overlap** with the Edge-IIoTset leakage papers. | Major | Related-work section must differentiate; do not claim to discover Edge-IIoTset leakage. |
| 4 | **Local Edge-IIoTset version.** The user's earlier project used a duplicate-leakage-corrected version; the documented artifacts may be absent or altered in the local copy. | Major | Verify which of the Tier 2 columns exist in the local files before relying on Tier 2 validation. |
| 5 | **Knockout retraining cost and group definition** can create researcher degrees of freedom. | Medium | Fixed grouping rule in pre-registration. |
| 6 | **Category mapping** between CICIoT2023 and CICIoMT2024 is a judgement call. | Medium | Document mapping, report coverage, ablate. |
| 7 | **Claim B "plausible"** is not yet measurable. | Medium | Define a metric before running (open item). |

Verdict: **PASS with conditions.** No Critical issue blocks Stage 2. Items 1 and 4 must be resolved in the protocol or pilot before any claim is drafted.

## 5. Open items before Stage 2 / the pilot
- Author sets: minimum meaningful AUC difference, false-alarm budget, seed count, pilot go/no-go criteria.
- Check the local Edge-IIoTset files for the four Tier 2 columns (item 4).
- Choose the MLP explainer (GradientSHAP / DeepSHAP / Kernel SHAP on a sample) and cost budget.
- Operationalize "plausible" for RQ3.
- Download CICIoMT2024 (UNB CIC page) and check its licence.
- Verify every reference in the survey's references.bib before citing.
