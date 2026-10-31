# Stage 4.5 final integrity check (numbers), 2026-10-31

- PASS: H1: S beats baseline in 0 of 9 
- PASS: H2: A adds in 0 of 9 
- PASS: best baseline is MI in 9 of 9 
- PASS: largest S-MI diff 0.045 (ciciomt mlp) 0.0449
- PASS: S-MI ciciomt lgbm .016, rf .019 
- PASS: S-MI ciciot lgbm and rf -0.013 
- PASS: largest A-S 0.048 (ciciot rf) 
- PASS: A<S for all three ciciomt 
- PASS: A<S for edge lgbm and mlp 
- PASS: seeds 30/15/30 
- PASS: Family A S range .960-1.000 
- PASS: Family B MI: ciciot .911, ciciomt .954, edge>=.999 
- PASS: C<S in 8 of 9 B cells; exception ciciot rf 
- PASS: weak plant ciciot S .994 MI .799 eta .794 
- PASS: transplanted S .507 MI .553 A .672 eta .954 
- PASS: redundant_ungrouped A<S (ciciomt) 
- PASS: redundant_ungrouped A<S (ciciot) 
- PASS: TPR S .875-1.000, eta .25-.34 
- PASS: FA range .028-.073, n=60, 28 above .05 28
- PASS: FA C edge rf .073, C ciciot rf .063, T ciciot lgbm .069, A ciciomt mlp .059 
- PASS: RFE FA .028-.030 everywhere 
- PASS: decoys S 3/27 cells 64/675 (np.int64(3), 27, np.int64(64), np.int64(675))
- PASS: decoys A 1/27 cells 28/675 (np.int64(1), 27, np.int64(28), np.int64(675))
- PASS: decoys T 9/18 cells 109/450 (np.int64(9), 18, np.int64(109), np.int64(450))
- PASS: S/A decoy flags all decoy_b90 
- PASS: specific decoy counts (15,25,24,28; T mlp ciciot decoy_a 15) 
- PASS: Tier2 eta AUC .990-.991, TPR 1.0 
- PASS: Tier2 S/C/A/MI/RFE TPR 0.0 
- PASS: Tier2 S AUC .732-.845 
- PASS: run counts 390/195/390 etc, 0 failures {'ciciot_lgbm': (390, 0), 'ciciot_rf': (390, 0), 'ciciot_mlp': (195, 0), 'edge_lgbm': (390, 0), 'edge_rf': (390, 0), 'edge_mlp': (195, 0), 'ciciomt_lgbm': (360, 0), 'ciciomt_rf': (360, 0), 'ciciomt_mlp': (180, 0)}
- PASS: calibration 9 logs x 80 ok, 0 failed 
- PASS: groups per clean run ciciot 32-33 32-33
- PASS: groups per clean run edge 35-38 35-38
- PASS: groups per clean run ciciomt 33-34 33-34
- PASS: Edge tier2: 4 planted groups/run, 39-42 groups 

Result: 35 PASS, 0 FAIL
