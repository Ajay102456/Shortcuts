# FULL STUDY summary (script-exported)

Thresholds: 95% percentile of clean calibration groups per (bench, model, score).

## Primary comparisons: sufficiency S vs best baseline on Family B (paired bootstrap, Holm over combos)
```
  bench model  n_seeds best_baseline  auc_S  auc_best_baseline  diff_S_minus_baseline  ci_lo  ci_hi     p  auc_A  diff_A_minus_S  ci2_lo  ci2_hi    p2  p_holm  p2_holm  S_beats_baseline  shap_concentration_adds
ciciomt  lgbm       30            mi  0.971              0.954                  0.016  0.011  0.023 0.000  0.930          -0.041  -0.044  -0.037 0.000   0.001    0.001             False                    False
ciciomt   mlp       15            mi  0.997              0.952                  0.045  0.037  0.053 0.000  0.992          -0.006  -0.009  -0.002 0.004   0.001    0.012             False                    False
ciciomt    rf       30            mi  0.973              0.954                  0.019  0.013  0.025 0.000  0.938          -0.035  -0.039  -0.032 0.000   0.001    0.001             False                    False
 ciciot  lgbm       30            mi  0.898              0.911                 -0.013 -0.014 -0.011 0.000  0.900           0.002  -0.001   0.005 0.274   0.001    0.548             False                    False
 ciciot   mlp       15            mi  0.916              0.910                  0.005  0.003  0.008 0.000  0.937           0.021   0.017   0.026 0.000   0.001    0.001             False                    False
 ciciot    rf       30            mi  0.898              0.911                 -0.013 -0.015 -0.012 0.000  0.946           0.048   0.047   0.049 0.000   0.001    0.001             False                    False
   edge  lgbm       30            mi  0.998              0.999                 -0.000 -0.001  0.000 0.720  0.976          -0.022  -0.023  -0.021 0.000   1.000    0.001             False                    False
   edge   mlp       15            mi  1.000              1.000                  0.000  0.000  0.000 1.000  0.989          -0.011  -0.020  -0.004 0.000   1.000    0.001             False                    False
   edge    rf       30            mi  0.998              0.999                 -0.000 -0.001  0.000 0.718  0.999           0.001  -0.000   0.002 0.722   1.000    0.722             False                    False
```

## Clean-control false-alarm rate (mean over evaluation seeds, bootstrap CI)
```
  bench model score   tau  fa_mean  fa_ci_lo  fa_ci_hi  n_seeds
ciciomt  lgbm     S 0.670    0.060     0.054     0.067       30
ciciomt  lgbm     C 0.097    0.048     0.043     0.053       30
ciciomt  lgbm     A 0.065    0.049     0.044     0.054       30
ciciomt  lgbm     T 0.526    0.046     0.041     0.051       30
ciciomt  lgbm   eta 0.765    0.056     0.052     0.060       30
ciciomt  lgbm    mi 0.963    0.056     0.051     0.061       30
ciciomt  lgbm   rfe 0.977    0.029     0.029     0.030       30
ciciomt   mlp     S 0.578    0.041     0.033     0.049       15
ciciomt   mlp     C 0.092    0.049     0.041     0.059       15
ciciomt   mlp     A 0.033    0.059     0.049     0.069       15
ciciomt   mlp     T 0.376    0.048     0.040     0.056       15
ciciomt   mlp   eta 0.765    0.057     0.051     0.063       15
ciciomt   mlp    mi 0.963    0.055     0.049     0.059       15
ciciomt   mlp   rfe 0.977    0.029     0.029     0.030       15
ciciomt    rf     S 0.675    0.054     0.050     0.058       30
ciciomt    rf     C 0.174    0.043     0.038     0.048       30
ciciomt    rf     A 0.119    0.042     0.037     0.047       30
ciciomt    rf     T 0.530    0.049     0.044     0.054       30
ciciomt    rf   eta 0.765    0.056     0.052     0.060       30
ciciomt    rf    mi 0.963    0.056     0.051     0.061       30
ciciomt    rf   rfe 0.977    0.029     0.029     0.030       30
 ciciot  lgbm     S 0.646    0.052     0.046     0.057       30
 ciciot  lgbm     C 0.154    0.056     0.052     0.060       30
 ciciot  lgbm     A 0.048    0.056     0.052     0.060       30
 ciciot  lgbm     T 0.397    0.069     0.059     0.079       30
 ciciot  lgbm   eta 0.813    0.055     0.049     0.061       30
 ciciot  lgbm    mi 0.944    0.050     0.044     0.055       30
 ciciot  lgbm   rfe 0.974    0.030     0.030     0.030       30
 ciciot   mlp     S 0.507    0.047     0.036     0.059       15
 ciciot   mlp     C 0.076    0.055     0.047     0.063       15
 ciciot   mlp     A 0.031    0.051     0.040     0.061       15
 ciciot   mlp     T 0.350    0.046     0.038     0.054       15
 ciciot   mlp   eta 0.813    0.055     0.048     0.061       15
 ciciot   mlp    mi 0.944    0.049     0.041     0.057       15
 ciciot   mlp   rfe 0.974    0.030     0.030     0.030       15
 ciciot    rf     S 0.664    0.056     0.051     0.061       30
 ciciot    rf     C 0.103    0.063     0.058     0.069       30
 ciciot    rf     A 0.061    0.053     0.047     0.058       30
 ciciot    rf     T 0.396    0.060     0.053     0.068       30
 ciciot    rf   eta 0.813    0.055     0.049     0.061       30
 ciciot    rf    mi 0.944    0.050     0.044     0.055       30
 ciciot    rf   rfe 0.974    0.030     0.030     0.030       30
   edge  lgbm     S 0.444    0.053     0.046     0.059       30
   edge  lgbm     C 0.133    0.056     0.053     0.058       30
   edge  lgbm     A 0.056    0.046     0.041     0.050       30
   edge  lgbm   eta 0.817    0.048     0.039     0.057       30
   edge  lgbm    mi 1.320    0.051     0.047     0.054       30
   edge  lgbm   rfe 0.977    0.028     0.028     0.028       30
   edge   mlp     S 0.217    0.043     0.026     0.061       15
   edge   mlp     C 0.152    0.041     0.034     0.048       15
   edge   mlp     A 0.027    0.048     0.037     0.060       15
   edge   mlp   eta 0.817    0.048     0.037     0.059       15
   edge   mlp    mi 1.320    0.054     0.050     0.056       15
   edge   mlp   rfe 0.977    0.028     0.028     0.028       15
   edge    rf     S 0.455    0.047     0.041     0.054       30
   edge    rf     C 0.094    0.073     0.066     0.081       30
   edge    rf     A 0.040    0.046     0.037     0.056       30
   edge    rf   eta 0.817    0.048     0.039     0.057       30
   edge    rf    mi 1.320    0.051     0.047     0.055       30
   edge    rf   rfe 0.977    0.028     0.028     0.028       30
```

Decoys flagged: see decoys.csv. Tier 3 flags on clean data: clean_flagged_groups_tier3.csv.
Per-condition AUC and TPR: auc_summary.csv. Pilot-informed design; see pre-registration section 14.
