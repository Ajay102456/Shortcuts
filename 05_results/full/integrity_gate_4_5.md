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
