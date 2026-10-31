| Signal | Symbol | Definition | Uses a trained model | Evaluated on |
|---|---|---|---|---|
| Sufficiency | S | Macro-F1 of a model trained on the group alone, divided by the full model's | yes | all groups |
| SHAP concentration | C | Group share of total mean absolute SHAP | yes | all groups |
| Audit score | A | C times S | yes | all groups |
| Necessity | R | Macro-F1 without the group, divided by the full model's | yes | top-10 groups by S |
| Transfer gap | T | In-domain minus cross-domain macro-F1 (CICIoT2023 and CICIoMT2024, five shared classes) | yes | CICIoT2023, CICIoMT2024 |
| Correlation ratio | eta | Square root of between-class over total variance | no | all groups |
| Mutual information | MI | Mutual information between feature and label | no | all groups |
| RFE rank | RFE | Rank in recursive feature elimination | wrapper | all groups |
