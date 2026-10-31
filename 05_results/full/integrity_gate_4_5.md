# Stage 4.5 final integrity gate, 2026-10-31

Verdict: PASS with open author items (no blocking integrity issue found).

## Checked and passed
- Numbers: 35 of 35 assertions pass (04_code/integrity_check_final.py; detail in integrity_gate_4_5_numbers.md). Covers H1/H2 outcome, differences and intervals, Family A/B AUCs, transplanted and weak-plant AUCs, TPRs, false-alarm range (60 cells, 28 above 0.05), decoy counts, Tier 2 results, run counts (0 failures), group counts.
- References: 75 of 75 verified (Crossref DOIs, arXiv API, publisher pages); each cited in the text.
- Pre-registration consistency: H1/H2 rules, margins, Holm, best-baseline rule and title rule applied as written; post-hoc and descriptive analyses labelled as such.
- Honesty: negative result reported as found; no hand-typed result numbers (tables and figures script-generated); no deviation entries; evaluation seeds run once.
- Disclosure added at this gate: the protocol was frozen locally with hashes, not in a public registry (Methods 4.7 and Limitations).

## Known residual risks
- Related-work sentences about the ~30 XAI/IDS papers are based on their titles (and for several, on corpus metadata), not full reading. Author should confirm each sentence against the paper.
- CICIoMT2024 data licence unverified by us (author reports CC article licence; Kaggle MIT mirror is not authoritative).
- The condensed Stage 3 review was a single-model simulation, not an independent panel.
- Software citations for SHAP library version and pandas are not in the reference list (LightGBM, scikit-learn, PyTorch are).

## Open author items
Author contributions, funding, conflicts of interest, AI-use statement confirmation, public repository link, optional public timestamp of the frozen protocol (for example an OSF upload of the freeze log), MDPI journal selection field.

## Addendum 2026-10-31: related-work check against local full texts
34 cited papers available in Papers_md were checked (abstracts and counts of SHAP, LIME, federated, distillation, adversarial, IIoT, dataset names). Errors found and fixed: (1) Pan et al. (Mathematics 2026) is about traffic-sign images for autonomous vehicles, not network traffic, and was cited as adversarial work on intrusion detectors; now described correctly. (2) "explainability in IoT detection" overstated the scope of the evaluation papers (some cover network intrusion or autonomous driving); reworded. (3) Kalakoti et al. was cited for "explanations as aids to trust" although it is a quantitative evaluation; replaced there by Moustafa et al. (still cited in 2.4). (4) Tavallaee et al. "inflated results" softened to "bias evaluation"; Ross et al. described as explanation constraints. Added: Alqahtani et al. use a leakage-free cross-validation protocol on CICIoT2023, TON_IoT and Edge-IIoTset. Not checked against full text: the ~39 papers not in the local corpus (verified by Crossref metadata, titles only).

## Addendum 2026-10-31 (review round 2)
Added 7 references on explanation-based shortcut detection (Anders et al. 2022; Teso and Kersting 2019; Schramowski et al. 2020; Du et al. 2023 via Crossref; Rieger et al., Singla and Feizi, Eyuboglu et al. via the arXiv API). Descriptions in the text are limited to what their titles and metadata state. Post-hoc sensitivity analysis added (04_code/sensitivity_no_ceiling.py, analysis/sensitivity_no_ceiling.csv): 0 of 6 combinations meet H1 or H2 after dropping the three Edge-IIoTset comparisons. Attribution of the four Tier 2 columns corrected to Dhaou only.
