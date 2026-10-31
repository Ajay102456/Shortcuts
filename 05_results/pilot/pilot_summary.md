# PILOT summary (script-exported; PILOT numbers, not final results)

Thresholds (95th percentile over pooled clean calibration groups): audit_A=0.04652, concentration_C=0.1642, sufficiency=0.6515, corr_eta=0.8149

## Mean group-level AUC / TPR at 5% FA threshold (5 evaluation seeds; mean, std)

```
                                       auc        tpr_at_fa5     
                                      mean    std       mean  std
condition           score                                        
plant_medium        audit_A          1.000  0.000        1.0  0.0
                    concentration_C  0.939  0.000        0.0  0.0
                    corr_eta         0.909  0.000        0.0  0.0
                    sufficiency      1.000  0.000        1.0  0.0
plant_strong        audit_A          1.000  0.000        1.0  0.0
                    concentration_C  1.000  0.000        1.0  0.0
                    corr_eta         0.970  0.000        1.0  0.0
                    sufficiency      1.000  0.000        1.0  0.0
plant_weak          audit_A          0.970  0.000        0.0  0.0
                    concentration_C  0.921  0.017        0.0  0.0
                    corr_eta         0.794  0.025        0.0  0.0
                    sufficiency      0.988  0.017        1.0  0.0
redundant_grouped   audit_A          1.000  0.000        1.0  0.0
                    concentration_C  0.939  0.000        0.0  0.0
                    corr_eta         0.909  0.000        0.0  0.0
                    sufficiency      1.000  0.000        1.0  0.0
redundant_ungrouped audit_A          0.892  0.016        0.0  0.0
                    concentration_C  0.725  0.015        0.0  0.0
                    corr_eta         0.909  0.000        0.0  0.0
                    sufficiency      1.000  0.000        1.0  0.0
```

## Clean-control false-alarm rate (evaluation seeds)

- audit_A: pooled 0.048; per seed [0.061, 0.03, 0.03, 0.061, 0.061]
- concentration_C: pooled 0.036; per seed [0.061, 0.03, 0.03, 0.03, 0.03]
- sufficiency: pooled 0.042; per seed [0.061, 0.03, 0.03, 0.061, 0.03]
- corr_eta: pooled 0.061; per seed [0.061, 0.061, 0.061, 0.061, 0.061]

Groups flagged by the audit in clean evaluation runs: 8 (see pilot_clean_flagged_groups.csv; Tier 3, unconfirmed).

## Decoy: groups containing the decoy flagged by the audit in 0 of 5 evaluation seeds

## Pre-registered go/no-go rule
- (i) audit AUC >= correlation AUC on medium AND strong plants: True (medium 1.000 vs 0.909; strong 1.000 vs 0.970)
- (ii) clean-control FA <= 5%: True (0.048)
- (iii) decoy flagged in 0 of 5 seeds: True
- **Decision: GO**
