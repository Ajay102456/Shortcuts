"""Build a fixed CICIoT2023 pool (8-class grouping) from the existing project loader.

Not a result: only fixes the data the pilot draws from. The loader reads the head
of each raw CSV (<= 3 x n_per_class rows per label group), so the pool is NOT a
uniform sample of the full corpus; this is a documented limitation.
"""
import os, sys, hashlib, json
import numpy as np

PROJECT = "/home/s/Documents/XAI-IOTEdge/Journal MDPI sensors"
sys.path.insert(0, PROJECT)
from src.data import load_ciciot2023  # noqa: E402

OUT = "/home/s/Documents/XAI-IOTEdge/Shortcut_Paper/data_cache/ciciot_pool.npz"
ds = load_ciciot2023(n_per_class=4000, label_grouping="8class", random_state=0)
X = np.vstack([ds.X_train, ds.X_test]).astype(np.float64)
y = np.concatenate([ds.y_train, ds.y_test])
np.savez_compressed(OUT, X=X, y=y, features=np.array(ds.feature_names), classes=np.array(ds.class_names))
h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
print("rows", X.shape, "classes", ds.class_names)
print("class counts", np.bincount(y).tolist())
print("features", len(ds.feature_names))
print(ds.feature_names)
print("pool sha256", h)
