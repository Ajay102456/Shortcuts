"""Full-study runner implementing 03_protocol/full_study_preregistration_DRAFT.md.

Benchmarks: ciciot, edge (ciciomt = stub until files exist). Models: lgbm, rf, mlp.
Modes: smoke (seed 1, tiny, temp dir, discarded) | timing (seed 1, timing only) |
       prep (calibration-only: decoy config, transplant tables) | calibrate | evaluate.
calibrate/evaluate refuse to run unless 05_results/full/freeze_log_full.md holds the
sha256 of this file and of the frozen pre-registration.
"""
import argparse, hashlib, json, os, sys, tempfile, time, warnings
import numpy as np, pandas as pd
import lightgbm as lgb, shap, torch, torch.nn as nn
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

ROOT = "/home/s/Documents/XAI-IOTEdge/Shortcut_Paper"
RES = f"{ROOT}/05_results/full"
PREREG = f"{ROOT}/03_protocol/full_study_preregistration.md"  # the frozen copy (created at freeze)
FREEZE = f"{RES}/freeze_log_full.md"
CICIOT_POOL = f"{ROOT}/data_cache/ciciot_pool.npz"
EDGE_CSV = ("/home/s/Documents/XAI-IOTEdge/Journal MDPI sensors/data/raw/Edge-IIoTset/Edge-IIoTset dataset/"
            "Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv")
CAL_SEEDS = list(range(1001, 1011))
EVAL_SEEDS = list(range(2001, 2031))
RHO = {"plant_weak": 0.6, "plant_medium": 0.8, "plant_strong": 0.95}
CONDITIONS = ["clean", "decoy_a", "decoy_b75", "decoy_b90", "exact_copy", "plant_weak", "plant_medium",
              "plant_strong", "redundant_grouped", "redundant_ungrouped", "entangled_0.5", "entangled_1.0",
              "transplanted"]
EDGE_ONLY = ["tier2_real"]
FAMILY_A = ["exact_copy", "plant_weak", "plant_medium", "plant_strong"]
TIER2 = ["dns.qry.name.len", "mqtt.conack.flags", "mqtt.protoname", "mqtt.topic"]
# 13 identifier/payload fields removed by the Edge-IIoTset leakage study; same rule applied here.
EDGE_DROP = ["frame.time", "ip.src_host", "ip.dst_host", "arp.dst.proto_ipv4", "arp.src.proto_ipv4",
             "http.file_data", "http.request.uri.query", "http.request.full_uri", "http.referer",
             "tcp.options", "tcp.payload", "tcp.srcport", "mqtt.msg", "Attack_label"]
# judgment table: CICIoT2023 class -> Edge-IIoTset class whose artifact value distribution is transplanted
TRANSPLANT_MAP = {"Benign": "Normal", "BruteForce": "Password", "DDoS": "DDoS_TCP", "DoS": "DDoS_HTTP",
                  "Mirai": "DDoS_UDP", "Recon": "Port_Scanning", "Spoofing": "MITM", "Web": "SQL_injection"}
GROUP_CUT = 0.10
TOPK_NECESSITY = 10
MLP_EVAL_SEEDS = 15
IOMT_DIR = "/home/s/Documents/XAI-IOTEdge/Journal MDPI sensors/data/raw/ciciomt2024"
IOMT_CACHE = {s: f"{ROOT}/data_cache/ciciomt_{s}_pool.npz" for s in ("train", "test")}
SHARED_CLASSES = ["Benign", "DDoS", "DoS", "Recon", "Spoofing"]  # mapped categories (MQTT-* has no counterpart)
TARGET_PER_CLASS = 1000


def iomt_category(fname):
    n = os.path.basename(fname)
    for pre, c in (("Benign", "Benign"), ("ARP", "Spoofing"), ("Recon", "Recon"), ("TCP_IP-DDoS", "DDoS"),
                   ("TCP_IP-DoS", "DoS"), ("MQTT", "MQTT")):
        if n.startswith(pre):
            return c
    raise ValueError(fname)


def build_iomt_cache(split, per_class=4000, per_file=6000):
    """Head-of-file capped sample (same limitation as the CICIoT2023 loader), z-scored per split."""
    import glob
    frames = {}
    for f in sorted(glob.glob(f"{IOMT_DIR}/{split}/*.csv")):
        frames.setdefault(iomt_category(f), []).append(pd.read_csv(f, nrows=per_file))
    parts, ys = [], []
    classes = sorted(frames)
    for i, c in enumerate(classes):
        d = pd.concat(frames[c], ignore_index=True).replace([np.inf, -np.inf], np.nan).dropna()
        d = d.sample(n=min(per_class, len(d)), random_state=0)
        parts.append(d); ys += [i] * len(d)
    X = pd.concat(parts, ignore_index=True)
    X = (X - X.mean()) / (X.std() + 1e-9)
    np.savez_compressed(IOMT_CACHE[split], X=X.values, y=np.array(ys), features=np.array(X.columns, dtype=str), classes=np.array(classes, dtype=str))
    return IOMT_CACHE[split]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------- data ----------------
def load_pool(bench):
    if bench == "ciciot":
        z = np.load(CICIOT_POOL)
        df = pd.DataFrame(z["X"], columns=list(z["features"]))
        return df, z["y"].astype(int), list(z["classes"])
    if bench == "edge":
        df = pd.read_csv(EDGE_CSV, low_memory=False)
        y_raw = df["Attack_type"].astype(str)
        df = df.drop(columns=["Attack_type"] + [c for c in EDGE_DROP if c in df.columns])
        keep = ~df.duplicated()
        df, y_raw = df[keep].reset_index(drop=True), y_raw[keep].reset_index(drop=True)
        classes = sorted(y_raw.unique())
        return df, y_raw.map({c: i for i, c in enumerate(classes)}).values.astype(int), classes
    if bench == "ciciomt":
        if not os.path.exists(IOMT_CACHE["train"]):
            build_iomt_cache("train")
        z = np.load(IOMT_CACHE["train"])
        return pd.DataFrame(z["X"], columns=list(z["features"])), z["y"].astype(int), list(z["classes"])
    raise ValueError(bench)


def get_target(bench):
    """Other-domain sample (shared 38 features, per-domain z-scored) for the transfer signal."""
    if bench == "ciciot":
        if not os.path.exists(IOMT_CACHE["test"]):
            build_iomt_cache("test")
        z = np.load(IOMT_CACHE["test"])
    elif bench == "ciciomt":
        z = np.load(CICIOT_POOL)
    else:
        return None
    df = pd.DataFrame(z["X"], columns=list(z["features"]))
    names = np.array(z["classes"])[z["y"].astype(int)]
    return df, names


def encode_strings(Xtr, Xte):
    """Target-agnostic ordinal encoding, fitted on the training split (unseen test values -> -1)."""
    Xtr, Xte = Xtr.copy(), Xte.copy()
    for c in Xtr.columns:
        if not pd.api.types.is_numeric_dtype(Xtr[c]):
            u = {v: i for i, v in enumerate(sorted(Xtr[c].astype(str).unique()))}
            Xtr[c] = Xtr[c].astype(str).map(u).astype(float)
            Xte[c] = Xte[c].astype(str).map(u).fillna(-1).astype(float)
    return Xtr, Xte


def transplant_tables():
    p = f"{RES}/transplant_tables.json"
    if os.path.exists(p):
        return json.load(open(p))
    df = pd.read_csv(EDGE_CSV, low_memory=False, usecols=TIER2 + ["Attack_type"])
    t = {}
    for c in TIER2:
        order = {v: i for i, v in enumerate(sorted(df[c].astype(str).unique()))}
        t[c] = {cls: [order[str(v)] for v in g[c].values] for cls, g in df.groupby("Attack_type")}
        t[c] = {k: np.random.default_rng(0).choice(v, size=min(len(v), 2000), replace=False).tolist() for k, v in t[c].items()}
    os.makedirs(RES, exist_ok=True)
    json.dump(t, open(p, "w"))
    return t


def plant(y, K, rng, cond, X_real, class_names):
    """Returns dict name->column for the condition (plants are functions of the true label)."""
    n = len(y)
    if cond == "exact_copy":
        return {"PLANT_0": rng.normal(size=K)[y]}
    if cond in RHO:
        keep = rng.random(n) < RHO[cond]
        ye = np.where(keep, y, (y + rng.integers(1, K, n)) % K)
        return {"PLANT_0": rng.normal(size=K)[ye]}
    if cond in ("redundant_grouped", "redundant_ungrouped"):
        ye = np.where(rng.random(n) < 0.8, y, (y + rng.integers(1, K, n)) % K)
        if cond == "redundant_grouped":
            base = rng.normal(size=K)[ye]
            return {f"PLANT_{j}": rng.uniform(0.5, 2) * base + rng.normal() for j in range(5)}
        return {f"PLANT_{j}": rng.normal(size=K)[ye] for j in range(5)}
    if cond.startswith("entangled"):
        beta = float(cond.split("_")[1])
        ye = np.where(rng.random(n) < 0.8, y, (y + rng.integers(1, K, n)) % K)
        j = rng.integers(0, X_real.shape[1])
        z = (X_real[:, j] - X_real[:, j].mean()) / (X_real[:, j].std() + 1e-9)
        return {"PLANT_0": rng.normal(size=K)[ye] + beta * z}
    if cond == "transplanted":
        t = transplant_tables()
        cols = {}
        for c in TIER2:
            v = np.zeros(n)
            for ci in range(K):
                m = np.where(y == ci)[0]
                pool = t[c][TRANSPLANT_MAP[class_names[ci]]]
                v[m] = rng.choice(pool, size=len(m))
            cols[f"PLANT_{c}"] = v
        return cols
    return {}


def make_data(bench, seed, cond, pool, npc, decoy_cfg):
    df, y_all, classes = pool
    K = len(classes)
    rng = np.random.default_rng(seed)
    idx = np.concatenate([rng.choice(np.where(y_all == c)[0], size=min(npc, (y_all == c).sum()), replace=False)
                          for c in range(K)])
    X, y = df.iloc[idx].reset_index(drop=True), y_all[idx]
    if bench == "edge" and cond != "tier2_real":
        X = X.drop(columns=[c for c in TIER2 if c in X.columns])  # clean base has no known artifacts
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    Xtr, Xte = encode_strings(Xtr, Xte)
    names = list(Xtr.columns)
    A, B = Xtr.values.astype(float), Xte.values.astype(float)
    if cond.startswith("decoy"):
        i, j = decoy_cfg[cond]
        z = lambda M, col: (M[:, col] - A[:, col].mean()) / (A[:, col].std() + 1e-9)
        A = np.column_stack([A, z(A, i) * z(A, j)]); B = np.column_stack([B, z(B, i) * z(B, j)])
        names.append("DECOY_" + cond)
    full_y = np.concatenate([ytr, yte])
    cols = plant(full_y, K, np.random.default_rng(seed * 1000 + 7), cond, np.vstack([A, B]), classes)
    if cols:
        ntr = len(ytr)
        for nm, v in cols.items():
            A = np.column_stack([A, v[:ntr]]); B = np.column_stack([B, v[ntr:]]); names.append(nm if nm.startswith("PLANT") else "PLANT_" + nm)
    return A, B, ytr, yte, names, K


# ---------------- models ----------------
class MLP(nn.Module):
    def __init__(self, f, k):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(f, 64), nn.ReLU(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, k))

    def forward(self, x):
        return self.net(x)


class Model:
    def __init__(self, kind, K, seed):
        self.kind, self.K, self.seed = kind, K, seed

    def fit(self, X, y):
        if self.kind == "lgbm":
            self.m = lgb.LGBMClassifier(n_estimators=150, num_leaves=31, max_depth=6, learning_rate=0.1,
                                        objective="multiclass", num_class=self.K, random_state=self.seed, verbosity=-1).fit(X, y)
        elif self.kind == "rf":
            self.m = RandomForestClassifier(n_estimators=100, max_depth=12, n_jobs=-1, random_state=self.seed).fit(X, y)
        else:
            torch.manual_seed(self.seed)
            self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
            Xt = torch.tensor((X - self.mu) / self.sd, dtype=torch.float32); yt = torch.tensor(y)
            self.m = MLP(X.shape[1], self.K); opt = torch.optim.Adam(self.m.parameters(), 1e-3)
            g = torch.Generator().manual_seed(self.seed)
            for _ in range(30):
                perm = torch.randperm(len(Xt), generator=g)
                for b in range(0, len(Xt), 256):
                    i = perm[b:b + 256]
                    opt.zero_grad(); nn.functional.cross_entropy(self.m(Xt[i]), yt[i]).backward(); opt.step()
        return self

    def predict(self, X):
        if self.kind != "mlp":
            return self.m.predict(X)
        with torch.no_grad():
            return self.m(torch.tensor((X - self.mu) / self.sd, dtype=torch.float32)).argmax(1).numpy()


def f1(kind, K, seed, Xtr, ytr, Xte, yte):
    return f1_score(yte, Model(kind, K, seed).fit(Xtr, ytr).predict(Xte), average="macro")


def mean_abs_shap(model, Xtr, Xte, seed):
    rng = np.random.default_rng(seed)
    n = {"lgbm": 1000, "rf": 300, "mlp": 200}[model.kind]
    sub = Xte[rng.choice(len(Xte), size=min(n, len(Xte)), replace=False)]
    if model.kind == "mlp":
        bg = torch.tensor((Xtr[rng.choice(len(Xtr), 100, replace=False)] - model.mu) / model.sd, dtype=torch.float32)
        sv = shap.GradientExplainer(model.m, bg).shap_values(torch.tensor((sub - model.mu) / model.sd, dtype=torch.float32))
    else:
        sv = shap.TreeExplainer(model.m).shap_values(sub, check_additivity=False)
    arr = np.stack([np.abs(s) for s in sv], -1) if isinstance(sv, list) else np.abs(np.asarray(sv))
    f = Xte.shape[1]
    if arr.ndim == 3 and arr.shape[1] != f:
        arr = np.moveaxis(arr, 0, -1) if arr.shape[2] == f else arr
    assert arr.ndim == 3 and arr.shape[1] == f, arr.shape
    return arr.mean(axis=(0, 2))


# ---------------- signals ----------------
def make_groups(A):
    c = np.nan_to_num(np.corrcoef(A, rowvar=False), nan=0.0); np.fill_diagonal(c, 1.0)
    d = 1 - np.abs(c); d = (d + d.T) / 2; np.fill_diagonal(d, 0.0)
    lab = fcluster(linkage(squareform(d, checks=False), method="average"), t=GROUP_CUT, criterion="distance")
    return [list(np.where(lab == g)[0]) for g in np.unique(lab)]


def eta(A, y, K):
    out = np.zeros(A.shape[1])
    for j in range(A.shape[1]):
        x = A[:, j]; tot = ((x - x.mean()) ** 2).sum()
        if tot > 0:
            out[j] = np.sqrt(sum((y == c).sum() * (x[y == c].mean() - x.mean()) ** 2 for c in range(K)) / tot)
    return out


def rfe_scores(A, y, seed):
    Z = (A - A.mean(0)) / (A.std(0) + 1e-9)
    sub = np.random.default_rng(seed).choice(len(Z), size=min(3000, len(Z)), replace=False)
    r = RFE(LogisticRegression(max_iter=200), n_features_to_select=1, step=0.2).fit(Z[sub], y[sub]).ranking_
    return 1.0 - (r - 1) / max(len(r) - 1, 1)


def transfer_scores(kind, seed, cond, A, B, ytr, yte, names, groups, classes, bench, cfg):
    """T_g = in-domain macro-F1 - cross-domain macro-F1 of a model trained on group g alone, restricted to the
    mapped categories. Planted columns have no label relation in the other domain (their values are a random
    permutation of the source column: a shortcut is a property of the source collection process). Decoys are
    recomputed from the target's own real features. Members absent from the target are dropped from the group;
    groups left with no member get NaN."""
    tgt = get_target(bench)
    out = np.full(len(groups), np.nan)
    if tgt is None:
        return out
    tdf, tnames = tgt
    rng = np.random.default_rng(seed * 31 + 5)
    mapped = [c for c in SHARED_CLASSES if c in classes]
    cmap = {classes.index(c): i for i, c in enumerate(mapped)}
    mtr, mte = np.isin(ytr, list(cmap)), np.isin(yte, list(cmap))
    ysr_tr = np.array([cmap[v] for v in ytr[mtr]]); ysr_te = np.array([cmap[v] for v in yte[mte]])
    rows = np.concatenate([rng.choice(np.where(tnames == c)[0], size=min(TARGET_PER_CLASS, (tnames == c).sum()), replace=False) for c in mapped])
    yt = np.array([mapped.index(v) for v in tnames[rows]])
    tsub = tdf.iloc[rows]
    zt = lambda col: (tsub[col].values - tsub[col].mean()) / (tsub[col].std() + 1e-9)
    for gi, g in enumerate(groups):
        keep, tcols = [], []
        for j in g:
            nm = names[j]
            if nm in tsub.columns:
                keep.append(j); tcols.append(tsub[nm].values)
            elif nm.startswith("PLANT_"):
                keep.append(j); tcols.append(rng.choice(np.concatenate([A[:, j], B[:, j]]), size=len(yt)))
            elif nm.startswith("DECOY_"):
                pi, pj = cfg["_names"][cond]
                if pi in tsub.columns and pj in tsub.columns:
                    keep.append(j); tcols.append(zt(pi) * zt(pj))
        if not keep:
            continue
        Tm = np.column_stack(tcols)
        m = Model(kind, len(mapped), seed).fit(A[mtr][:, keep], ysr_tr)
        f_in = f1_score(ysr_te, m.predict(B[mte][:, keep]), average="macro")
        f_tr = f1_score(yt, m.predict(Tm), average="macro")
        out[gi] = f_in - f_tr
    return out


def run_one(bench, kind, seed, cond, pool, npc, decoy_cfg):
    A, B, ytr, yte, names, K = make_data(bench, seed, cond, pool, npc, decoy_cfg)
    f = A.shape[1]
    full = Model(kind, K, seed).fit(A, ytr)
    f1_full = f1_score(yte, full.predict(B), average="macro")
    groups = make_groups(A)
    msh = mean_abs_shap(full, A, B, seed)
    C = np.array([msh[g].sum() for g in groups]) / msh.sum()
    et = eta(A, ytr, K)
    mi = mutual_info_classif(A[:3000], ytr[:3000], random_state=seed) if len(A) else np.zeros(f)
    rf_ = rfe_scores(A, ytr, seed)
    S = np.array([f1(kind, K, seed, A[:, g], ytr, B[:, g], yte) / f1_full for g in groups])
    R = np.full(len(groups), np.nan)  # necessity: only the top-TOPK_NECESSITY groups by sufficiency (rank-based, pre-specified)
    for gi in np.argsort(-S)[:TOPK_NECESSITY]:
        rest = [j for j in range(f) if j not in groups[gi]]
        if rest:
            R[gi] = f1(kind, K, seed, A[:, rest], ytr, B[:, rest], yte) / f1_full
    T = transfer_scores(kind, seed, cond, A, B, ytr, yte, names, groups, pool[2], bench, decoy_cfg)
    rows = []
    for gi, g in enumerate(groups):
        mem = [names[j] for j in g]
        rows.append(dict(bench=bench, model=kind, seed=seed, condition=cond, group=gi, size=len(g), members="|".join(mem),
                         planted=any(m.startswith("PLANT_") for m in mem) or (cond == "tier2_real" and any(m in TIER2 for m in mem)),
                         has_decoy=any(m.startswith("DECOY_") for m in mem), C=C[gi], S=S[gi], A=C[gi] * S[gi], R=R[gi],
                         eta=max(et[j] for j in g), mi=max(mi[j] for j in g), rfe=max(rf_[j] for j in g),
                         T=T[gi],
                         f1_full=f1_full, n_features=f, n_groups=len(groups)))
    return rows


def prep_decoys(bench, pool, npc, out=RES):
    """Calibration-only: choose decoy feature pairs from calibration seed 1001 clean data (LightGBM)."""
    A, B, ytr, yte, names, K = make_data(bench, CAL_SEEDS[0], "clean", pool, npc, {})
    et = eta(A, ytr, K)
    full = Model("lgbm", K, CAL_SEEDS[0]).fit(A, ytr)
    msh = mean_abs_shap(full, A, B, CAL_SEEDS[0])
    num = {c for c in pool[0].columns if pd.api.types.is_numeric_dtype(pool[0][c])}  # natively numeric only
    cand = [i for i, n in enumerate(names) if n in num]
    top_eta = [cand[i] for i in np.argsort(-et[cand])[:2]]
    order = [cand[i] for i in np.argsort(msh[cand])]
    p = lambda q: order[int(q * (len(order) - 1))]
    cfg = {"decoy_a": [int(top_eta[0]), int(top_eta[1])],
           "decoy_b75": [int(p(0.75)), int(p(0.60))], "decoy_b90": [int(p(0.90)), int(p(0.60))]}
    cfg["_names"] = {k: [names[i] for i in v] for k, v in cfg.items()}
    os.makedirs(out, exist_ok=True)
    json.dump(cfg, open(f"{out}/decoy_config_{bench}.json", "w"), indent=1)
    return cfg


def check_freeze():
    txt = open(FREEZE).read()
    for k, p in {"prereg": PREREG, "code": __file__}.items():
        if sha(p) not in txt:
            sys.exit(f"REFUSING: {k} sha256 not in {FREEZE}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "timing", "prep", "calibrate", "evaluate"], required=True)
    ap.add_argument("--bench", choices=["ciciot", "edge", "ciciomt"], default="ciciot")
    ap.add_argument("--model", choices=["lgbm", "rf", "mlp"], default="lgbm")
    ap.add_argument("--seeds", type=int, default=0, help="limit number of seeds (only for non-frozen modes)")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    pool = load_pool(a.bench)
    npc = 800 if a.bench == "edge" else 1500
    conds = ([c for c in CONDITIONS if c != "transplanted"] + EDGE_ONLY) if a.bench == "edge" else ([c for c in CONDITIONS if c != "transplanted"] if a.bench == "ciciomt" else list(CONDITIONS))
    if a.mode == "prep":
        print(json.dumps(prep_decoys(a.bench, pool, npc)["_names"], indent=1)); return
    cfg_path = f"{RES}/decoy_config_{a.bench}.json"
    if a.mode in ("smoke", "timing"):
        npc = 150 if a.mode == "smoke" else npc
        out = tempfile.mkdtemp(prefix="full_smoke_") if a.mode == "smoke" else RES
        cfg = prep_decoys(a.bench, pool, npc, out) if a.mode == "smoke" else json.load(open(cfg_path))
        seeds = [1]
        if a.mode == "timing":
            conds = ["clean", "plant_medium", "redundant_ungrouped"]
        if a.mode == "smoke":
            conds = ["clean", "decoy_a", "plant_medium", "entangled_1.0"] + (EDGE_ONLY if a.bench == "edge" else ([] if a.bench == "ciciomt" else ["transplanted"]))
    else:
        check_freeze()
        cfg, out = json.load(open(cfg_path)), RES
        seeds = (CAL_SEEDS if a.mode == "calibrate" else (EVAL_SEEDS[:MLP_EVAL_SEEDS] if a.model == "mlp" else EVAL_SEEDS))
        conds = (["clean"] + FAMILY_A + ["decoy_a", "decoy_b75", "decoy_b90"]) if a.mode == "calibrate" else conds
    rows, log = [], []
    for s in seeds:
        for c in conds:
            t0 = time.time()
            try:
                rows += run_one(a.bench, a.model, s, c, pool, npc, cfg)
                log.append(dict(bench=a.bench, model=a.model, seed=s, condition=c, status="ok", seconds=round(time.time() - t0, 1)))
            except Exception as e:
                log.append(dict(bench=a.bench, model=a.model, seed=s, condition=c, status=f"FAILED: {type(e).__name__}: {e}"))
            print(log[-1], flush=True)
    tag = {"smoke": "smoke", "timing": "timing", "calibrate": "calibration", "evaluate": "evaluation"}[a.mode]
    stem = f"{a.bench}_{a.model}_{tag}"
    if a.mode != "timing":
        pd.DataFrame(rows).to_csv(f"{out}/group_scores_{stem}.csv", index=False)
    pd.DataFrame(log).to_csv(f"{out}/run_log_{stem}.csv", index=False)
    json.dump(dict(mode=a.mode, versions=dict(lightgbm=lgb.__version__, shap=shap.__version__, torch=torch.__version__,
              numpy=np.__version__, pandas=pd.__version__), code_sha256=sha(__file__),
              utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), open(f"{out}/manifest_{stem}.json", "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
