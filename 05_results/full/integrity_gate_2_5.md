# Stage 2.5 integrity gate (draft v1), 2026-10-31
- Numbers: tables exported by 04_code/make_tables.py and analyze_full.py. Prose numbers re-checked against exports for sections 4.1, 4.5 (FA range and decoy counts recomputed from CSVs). Error found and fixed: draft claimed S/A almost never flagged decoys and FA mostly 4-7%; actual: S flagged decoy_b90 in 3 of 27 cells, A in 1, FA range 0.028-0.073. 
- Still to check at next pass: sections 4.2-4.4 and 5 wording vs tables (spot-checked: Family A S range, transplanted AUCs, tier2 eta/TPR).
- References 1-9 verified (see draft section 9). Licence for CICIoMT2024 unconfirmed.
- Open: Introduction and Related Work unwritten; AI-use statement to be confirmed against Sensors policy.
- 2026-10-31 (draft v2, 75 refs): fixed "63 signal-cell values" to 60 (9 cells x 7 signals minus T undefined on Edge-IIoTset); removed an unsupported explanation of RFE false-alarm rate; split Table 3 into H1/H2 tables. All 75 references verified via Crossref (DOIs), arXiv API or publisher pages; licence of CICIoMT2024 still unconfirmed.
- 2026-10-31: CICIoMT2024 licence: author reports article is open access (CC) and Kaggle mirrors list MIT; neither verified by me (UNB page states no licence; ScienceDirect page not reached). Data Availability statement worded accordingly; confirm with dataset owners before redistributing.
