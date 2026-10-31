"""Full-study analysis exactly as in the frozen pre-registration (sections 6, 8, 14).
Reads group_scores_{bench}_{model}_{calibration,evaluation}.csv from --dir; writes CSVs + summary.md
into <dir>/analysis. All numbers are script-exported."""
import argparse, glob, os
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score

FAMILY_B = ["redundant_grouped", "redundant_ungrouped", "entangled_0.5", "entangled_1.0", "transplanted"]
FAMILY_A = ["exact_copy", "plant_weak", "plant_medium", "plant_strong"]
DECOYS = ["decoy_a", "decoy_b75", "decoy_b90"]
SCORES = ["S", "C", "A", "T", "R", "eta", "mi", "rfe"]  # S primary; A = C*S; T transfer; R necessity (top-10 only)
BASELINES = ["eta", "mi", "rfe"]
THRESH_SCORES = ["S", "C", "A", "T", "eta", "mi", "rfe"]  # R is partial (top-10), no FA threshold
MIN_GAP, FA, N_BOOT = 0.05, 0.95, 10000

ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); a = ap.parse_args()
OUT = f"{a.dir}/analysis"; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(12345)


def load(tag):
    fr = []
    for f in sorted(glob.glob(f"{a.dir}/group_scores_*_{tag}.csv")):
        d = pd.read_csv(f)
        if len(d):
            fr.append(d)
    return pd.concat(fr, ignore_index=True)


cal, ev = load("calibration"), load("evaluation")
combos = sorted(set(zip(ev.bench, ev.model)))
tau = {}
for (b, m) in combos:
    c = cal[(cal.bench == b) & (cal.model == m) & (cal.condition == "clean")]
    for s in THRESH_SCORES:
        v = c[s].dropna()
        tau[(b, m, s)] = np.percentile(v, FA * 100) if len(v) else np.nan


def auc_of(g, s):
    g = g[g[s].notna()]
    return roc_auc_score(g.planted, g[s]) if g.planted.nunique() == 2 else np.nan


rows = []
for (b, m, cond, seed), g in ev.groupby(["bench", "model", "condition", "seed"]):
    if cond in FAMILY_A + FAMILY_B + ["tier2_real"]:
        for s in SCORES:
            tpr = float((g[g.planted][s] > tau[(b, m, s)]).mean()) if s in THRESH_SCORES and g.planted.any() else np.nan
            rows.append(dict(bench=b, model=m, condition=cond, seed=seed, score=s, auc=auc_of(g, s), tpr_at_fa5=tpr))
auc = pd.DataFrame(rows)
auc.to_csv(f"{OUT}/auc_per_seed.csv", index=False)
auc.groupby(["bench", "model", "condition", "score"])[["auc", "tpr_at_fa5"]].agg(["mean", "std", "count"]).round(3).to_csv(f"{OUT}/auc_summary.csv")


def boot_p(d):
    d = np.asarray(d, float); d = d[~np.isnan(d)]
    if len(d) < 2:
        return np.nan, np.nan, np.nan, np.nan
    bs = rng.choice(d, size=(N_BOOT, len(d)), replace=True).mean(1)
    p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1.0 / N_BOOT)
    return d.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), p


def holm(ps):
    ps = np.array(ps, float); order = np.argsort(ps); adj = np.empty_like(ps); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (len(ps) - rank) * ps[i]); adj[i] = min(1.0, run)
    return adj


# per-seed Family B mean AUC for each score
fb = auc[auc.condition.isin(FAMILY_B)].groupby(["bench", "model", "seed", "score"]).auc.mean().reset_index()
prim = []
for (b, m) in combos:
    x = fb[(fb.bench == b) & (fb.model == m)].pivot(index="seed", columns="score", values="auc")
    if "S" not in x:
        continue
    best = x[BASELINES].mean().idxmax()
    mean_d, lo, hi, p = boot_p(x["S"] - x[best])
    mean_d2, lo2, hi2, p2 = boot_p(x["A"] - x["S"])
    prim.append(dict(bench=b, model=m, n_seeds=len(x), best_baseline=best, auc_S=x["S"].mean(), auc_best_baseline=x[best].mean(),
                     diff_S_minus_baseline=mean_d, ci_lo=lo, ci_hi=hi, p=p,
                     auc_A=x["A"].mean(), diff_A_minus_S=mean_d2, ci2_lo=lo2, ci2_hi=hi2, p2=p2))
prim = pd.DataFrame(prim)
if len(prim):
    prim["p_holm"] = holm(prim.p.fillna(1)); prim["p2_holm"] = holm(prim.p2.fillna(1))
    prim["S_beats_baseline"] = (prim.diff_S_minus_baseline >= MIN_GAP) & (prim.p_holm < 0.05)
    prim["shap_concentration_adds"] = (prim.diff_A_minus_S >= MIN_GAP) & (prim.p2_holm < 0.05)
prim.round(4).to_csv(f"{OUT}/primary_comparisons.csv", index=False)

# clean-control false alarms and decoys
fa_rows = []
for (b, m) in combos:
    cl = ev[(ev.bench == b) & (ev.model == m) & (ev.condition == "clean")]
    for s in THRESH_SCORES:
        per = [float((g[s].dropna() > tau[(b, m, s)]).mean()) for _, g in cl.groupby("seed") if g[s].notna().any()]
        if per:
            mean_fa, lo, hi, _ = boot_p(per)
            fa_rows.append(dict(bench=b, model=m, score=s, tau=tau[(b, m, s)], fa_mean=np.mean(per), fa_ci_lo=lo, fa_ci_hi=hi, n_seeds=len(per)))
pd.DataFrame(fa_rows).round(4).to_csv(f"{OUT}/clean_false_alarms.csv", index=False)
flag_rows = []
for (b, m) in combos:
    cl = ev[(ev.bench == b) & (ev.model == m) & (ev.condition == "clean")]
    f = cl[cl.S > tau[(b, m, "S")]]
    flag_rows.append(f.groupby("members").agg(n_seeds=("seed", "nunique"), mean_S=("S", "mean"), mean_C=("C", "mean"), mean_T=("T", "mean")).reset_index().assign(bench=b, model=m))
pd.concat(flag_rows).round(4).to_csv(f"{OUT}/clean_flagged_groups_tier3.csv", index=False)
dec = []
for (b, m) in combos:
    for c in DECOYS:
        d = ev[(ev.bench == b) & (ev.model == m) & (ev.condition == c) & ev.has_decoy]
        for s in ["S", "A", "T"]:
            if len(d) and d[s].notna().any():
                dec.append(dict(bench=b, model=m, decoy=c, score=s, seeds_flagged=int((d[s] > tau[(b, m, s)]).sum()), n_seeds=d.seed.nunique()))
pd.DataFrame(dec).to_csv(f"{OUT}/decoys.csv", index=False)

L = ["# FULL STUDY summary (script-exported)", "", f"Thresholds: {FA:.0%} percentile of clean calibration groups per (bench, model, score).", "",
     "## Primary comparisons: sufficiency S vs best baseline on Family B (paired bootstrap, Holm over combos)", "```",
     prim.round(3).to_string(index=False) if len(prim) else "no data", "```", "",
     "## Clean-control false-alarm rate (mean over evaluation seeds, bootstrap CI)", "```",
     pd.DataFrame(fa_rows).round(3).to_string(index=False), "```", "", "Decoys flagged: see decoys.csv. Tier 3 flags on clean data: clean_flagged_groups_tier3.csv.",
     "Per-condition AUC and TPR: auc_summary.csv. Pilot-informed design; see pre-registration section 14."]
open(f"{OUT}/summary.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
