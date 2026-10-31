"""Pilot: attribution-based shortcut audit on CICIoT2023 + LightGBM.

Implements 03_protocol/pilot_preregistration.md exactly. Modes:
  smoke      seed 1, reduced size, writes to a temp dir (output discarded)
  calibrate  seeds 101-105, clean condition only
  evaluate   seeds 201-205, all conditions
calibrate/evaluate refuse to run unless the freeze log holds the sha256 of this
file and of the pre-registration.
"""
import argparse, hashlib, json, os, sys, tempfile, time, warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
import shap
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

ROOT = "/home/s/Documents/XAI-IOTEdge/Shortcut_Paper"
POOL = f"{ROOT}/data_cache/ciciot_pool.npz"
PREREG = f"{ROOT}/03_protocol/pilot_preregistration.md"
RES = f"{ROOT}/05_results/pilot"
FREEZE = f"{RES}/freeze_log.md"

CAL_SEEDS = [101, 102, 103, 104, 105]
EVAL_SEEDS = [201, 202, 203, 204, 205]
CONDITIONS = ["clean", "decoy", "plant_weak", "plant_medium", "plant_strong",
              "redundant_grouped", "redundant_ungrouped"]
RHO = {"plant_weak": 0.6, "plant_medium": 0.8, "plant_strong": 0.95}
K = 8
N_PER_CLASS = 1500
SHAP_ROWS = 1000
GROUP_CUT = 0.10
TOPK_RESIL = 5


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def lgbm(seed):
    return lgb.LGBMClassifier(n_estimators=150, num_leaves=31, max_depth=6, learning_rate=0.1,
                              objective="multiclass", num_class=K, random_state=seed, verbosity=-1)


def macro_f1(model, Xtr, ytr, Xte, yte):
    model.fit(Xtr, ytr)
    return f1_score(yte, model.predict(Xte), average="macro")


def plant_columns(y, rng, condition):
    """Returns (list of columns, list of names). Plants are a function of the true label."""
    n = len(y)
    if condition in RHO:
        rho = RHO[condition]
        m = rng.normal(size=K)
        keep = rng.random(n) < rho
        y_eff = np.where(keep, y, (y + rng.integers(1, K, n)) % K)
        return [m[y_eff]], ["PLANT_0"]
    if condition in ("redundant_grouped", "redundant_ungrouped"):
        keep = rng.random(n) < 0.8
        y_eff = np.where(keep, y, (y + rng.integers(1, K, n)) % K)
        cols = []
        if condition == "redundant_grouped":
            base = rng.normal(size=K)[y_eff]
            for _ in range(5):
                a = rng.uniform(0.5, 2.0)
                b = rng.normal()
                cols.append(a * base + b)
        else:
            for _ in range(5):
                cols.append(rng.normal(size=K)[y_eff])
        return cols, [f"PLANT_{j}" for j in range(5)]
    return [], []


def make_data(seed, condition, pool, n_per_class):
    X_pool, y_pool, feats = pool["X"], pool["y"], list(pool["features"])
    rng = np.random.default_rng(seed)
    idx = np.concatenate([rng.choice(np.where(y_pool == c)[0], size=n_per_class, replace=False)
                          for c in range(K)])
    X, y = X_pool[idx].copy(), y_pool[idx].copy()
    names = list(feats)
    if condition == "decoy":
        X = np.column_stack([X, X[:, names.index("Max")] - X[:, names.index("Min")]])
        names.append("DECOY_MaxMinusMin")
    cols, new = plant_columns(y, np.random.default_rng(seed * 1000 + 7), condition)
    if cols:
        X = np.column_stack([X] + cols)
        names += new
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    return Xtr, Xte, ytr, yte, names


def make_groups(Xtr):
    c = np.corrcoef(Xtr, rowvar=False)
    c = np.nan_to_num(c, nan=0.0)
    np.fill_diagonal(c, 1.0)
    d = 1.0 - np.abs(c)
    d = (d + d.T) / 2
    np.fill_diagonal(d, 0.0)
    Z = linkage(squareform(d, checks=False), method="average")
    lab = fcluster(Z, t=GROUP_CUT, criterion="distance")
    return [list(np.where(lab == g)[0]) for g in np.unique(lab)]


def eta(Xtr, ytr):
    out = np.zeros(Xtr.shape[1])
    for j in range(Xtr.shape[1]):
        x = Xtr[:, j]
        tot = ((x - x.mean()) ** 2).sum()
        if tot <= 0:
            continue
        bet = sum((ytr == c).sum() * (x[ytr == c].mean() - x.mean()) ** 2 for c in range(K))
        out[j] = np.sqrt(bet / tot)
    return out


def mean_abs_shap(model, Xte, seed):
    rng = np.random.default_rng(seed)
    sub = Xte[rng.choice(len(Xte), size=min(SHAP_ROWS, len(Xte)), replace=False)]
    sv = shap.TreeExplainer(model).shap_values(sub, check_additivity=False)
    if isinstance(sv, list):
        arr = np.stack([np.abs(s) for s in sv], axis=-1)  # (n, f, c)
    else:
        arr = np.abs(np.asarray(sv))
        f = Xte.shape[1]
        if arr.ndim == 3 and arr.shape[1] != f:
            arr = np.moveaxis(arr, 0, -1) if arr.shape[2] == f else arr
    assert arr.ndim == 3 and arr.shape[1] == Xte.shape[1], arr.shape
    return arr.mean(axis=(0, 2))


def run_one(seed, condition, pool, n_per_class):
    Xtr, Xte, ytr, yte, names = make_data(seed, condition, pool, n_per_class)
    f = Xtr.shape[1]
    full = lgbm(seed)
    f1_full = macro_f1(full, Xtr, ytr, Xte, yte)
    groups = make_groups(Xtr)
    msh = mean_abs_shap(full, Xte, seed)
    C = np.array([msh[g].sum() for g in groups]) / msh.sum()
    et = eta(Xtr, ytr)
    suff = np.array([macro_f1(lgbm(seed), Xtr[:, g], ytr, Xte[:, g], yte) / f1_full for g in groups])
    A = C * suff
    resil = np.full(len(groups), np.nan)
    for gi in np.argsort(-A)[:TOPK_RESIL]:
        rest = [j for j in range(f) if j not in groups[gi]]
        resil[gi] = macro_f1(lgbm(seed), Xtr[:, rest], ytr, Xte[:, rest], yte) / f1_full if rest else np.nan
    rows = []
    for gi, g in enumerate(groups):
        mem = [names[j] for j in g]
        rows.append(dict(seed=seed, condition=condition, group=gi, size=len(g), members="|".join(mem),
                         planted=any(m.startswith("PLANT_") for m in mem),
                         has_decoy=any(m.startswith("DECOY_") for m in mem),
                         C=C[gi], Suff=suff[gi], A=A[gi], corr_eta=max(et[j] for j in g),
                         Resil=resil[gi], f1_full=f1_full, n_features=f, n_groups=len(groups)))
    return rows


def check_freeze():
    txt = open(FREEZE).read()
    need = {"prereg": sha256(PREREG), "code": sha256(__file__)}
    for k, v in need.items():
        if v not in txt:
            sys.exit(f"REFUSING: {k} sha256 {v} not in freeze log. Record it before running real seeds.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "calibrate", "evaluate"], required=True)
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    pool = np.load(POOL)
    if a.mode == "smoke":
        out = tempfile.mkdtemp(prefix="pilot_smoke_")
        seeds, conds, npc = [1], ["clean", "plant_medium", "redundant_ungrouped", "decoy"], 200
    else:
        check_freeze()
        out = RES
        seeds = CAL_SEEDS if a.mode == "calibrate" else EVAL_SEEDS
        conds = ["clean"] if a.mode == "calibrate" else CONDITIONS
        npc = N_PER_CLASS
    all_rows, log = [], []
    for s in seeds:
        for c in conds:
            t0 = time.time()
            try:
                all_rows += run_one(s, c, pool, npc)
                log.append(dict(seed=s, condition=c, status="ok", seconds=round(time.time() - t0, 1)))
            except Exception as e:  # logged, never silently dropped
                log.append(dict(seed=s, condition=c, status=f"FAILED: {type(e).__name__}: {e}"))
            print(log[-1], flush=True)
    tag = {"smoke": "smoke", "calibrate": "calibration", "evaluate": "evaluation"}[a.mode]
    pd.DataFrame(all_rows).to_csv(f"{out}/group_scores_{tag}.csv", index=False)
    pd.DataFrame(log).to_csv(f"{out}/run_log_{tag}.csv", index=False)
    json.dump(dict(mode=a.mode, versions=dict(lightgbm=lgb.__version__, shap=shap.__version__,
                                             numpy=np.__version__, pandas=pd.__version__),
                   pool_sha256=sha256(POOL), code_sha256=sha256(__file__), prereg_sha256=sha256(PREREG),
                   utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
              open(f"{out}/manifest_{tag}.json", "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
