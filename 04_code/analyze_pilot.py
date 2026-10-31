"""Pilot analysis exactly as in 03_protocol/pilot_preregistration.md sections 6-7.
Reads group_scores_calibration.csv and group_scores_evaluation.csv; writes
pilot_summary.csv and pilot_summary.md (all numbers script-exported)."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

RES = "/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/05_results/pilot"
cal = pd.read_csv(f"{RES}/group_scores_calibration.csv")
ev = pd.read_csv(f"{RES}/group_scores_evaluation.csv")
SCORES = {"audit_A": "A", "concentration_C": "C", "sufficiency": "Suff", "corr_eta": "corr_eta"}
tau = {k: np.percentile(cal[v], 95) for k, v in SCORES.items()}

rows = []
for cond in ["plant_weak", "plant_medium", "plant_strong", "redundant_grouped", "redundant_ungrouped"]:
    for seed, g in ev[ev.condition == cond].groupby("seed"):
        for name, col in SCORES.items():
            rows.append(dict(condition=cond, seed=seed, score=name,
                             auc=roc_auc_score(g.planted, g[col]) if g.planted.nunique() == 2 else np.nan,
                             tpr_at_fa5=float((g[g.planted][col] > tau[name]).mean())))
auc = pd.DataFrame(rows)
auc.to_csv(f"{RES}/pilot_auc_per_seed.csv", index=False)
mean_auc = auc.groupby(["condition", "score"])[["auc", "tpr_at_fa5"]].agg(["mean", "std"]).round(3)
mean_auc.to_csv(f"{RES}/pilot_auc_summary.csv")

clean = ev[ev.condition == "clean"]
fa = {name: dict(pooled=float((clean[col] > tau[name]).mean()),
                 per_seed=[round(float((g[col] > tau[name]).mean()), 3) for _, g in clean.groupby("seed")])
      for name, col in SCORES.items()}
flagged_clean = clean[clean.A > tau["audit_A"]][["seed", "members", "C", "Suff", "A"]]
flagged_clean.to_csv(f"{RES}/pilot_clean_flagged_groups.csv", index=False)

dec = ev[(ev.condition == "decoy") & ev.has_decoy]
dec_flagged = int((dec.A > tau["audit_A"]).sum())
dec[["seed", "members", "C", "Suff", "A"]].to_csv(f"{RES}/pilot_decoy_groups.csv", index=False)

m = lambda c, s: auc[(auc.condition == c) & (auc.score == s)].auc.mean()
cond_i = all(m(c, "audit_A") >= m(c, "corr_eta") for c in ["plant_medium", "plant_strong"])
cond_ii = fa["audit_A"]["pooled"] <= 0.05
cond_iii = dec_flagged == 0
go = cond_i and cond_ii and cond_iii

L = ["# PILOT summary (script-exported; PILOT numbers, not final results)", "",
     "Thresholds (95th percentile over pooled clean calibration groups): " +
     ", ".join(f"{k}={v:.4g}" for k, v in tau.items()), "",
     "## Mean group-level AUC / TPR at 5% FA threshold (5 evaluation seeds; mean, std)", "",
     "```", mean_auc.to_string(), "```", "",
     "## Clean-control false-alarm rate (evaluation seeds)", ""]
L += [f"- {k}: pooled {v['pooled']:.3f}; per seed {v['per_seed']}" for k, v in fa.items()]
L += ["", f"Groups flagged by the audit in clean evaluation runs: {len(flagged_clean)} (see pilot_clean_flagged_groups.csv; Tier 3, unconfirmed).", "",
      f"## Decoy: groups containing the decoy flagged by the audit in {dec_flagged} of {dec.seed.nunique()} evaluation seeds", "",
      "## Pre-registered go/no-go rule",
      f"- (i) audit AUC >= correlation AUC on medium AND strong plants: {cond_i} "
      f"(medium {m('plant_medium','audit_A'):.3f} vs {m('plant_medium','corr_eta'):.3f}; "
      f"strong {m('plant_strong','audit_A'):.3f} vs {m('plant_strong','corr_eta'):.3f})",
      f"- (ii) clean-control FA <= 5%: {cond_ii} ({fa['audit_A']['pooled']:.3f})",
      f"- (iii) decoy flagged in 0 of 5 seeds: {cond_iii}",
      f"- **Decision: {'GO' if go else 'NO-GO'}**"]
open(f"{RES}/pilot_summary.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
