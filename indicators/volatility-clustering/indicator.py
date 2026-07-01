from tg_scripting import *
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

indicator("Volatility Clustering (DBSCAN)", overlay=False)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
ret_len = input.int(10, "Returns Lookback", minval=3, maxval=50)
vol_len = input.int(20, "Volume MA Length", minval=5, maxval=100)
eps_val = input.float(0.8, "DBSCAN Epsilon", minval=0.1, maxval=3.0)
min_samples = input.int(5, "Min Samples", minval=2, maxval=20)
smoothing = input.int(3, "Cluster Smoothing", minval=1, maxval=10)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Transitions")
label_cooldown = input.int(15, "Label Cooldown Bars", minval=5, maxval=50)

close_arr = np.array(close, dtype=np.float64)
high_arr = np.array(high, dtype=np.float64)
low_arr = np.array(low, dtype=np.float64)
vol_arr = np.array(volume, dtype=np.float64)
n = len(close_arr)

# Feature 1: ATR%
atr_raw = ta.atr(high, low, close, atr_len)
atr_arr = np.array(atr_raw, dtype=np.float64)
atr_pct = (atr_arr / np.maximum(close_arr, 1e-10)) * 100.0

# Feature 2: Return magnitude
ret_mag = np.zeros(n)
for i in range(ret_len, n):
    ret_mag[i] = abs((close_arr[i] / close_arr[i - ret_len] - 1.0) * 100.0)

# Feature 3: Volume change ratio
vol_ma = np.array(ta.sma(volume, vol_len), dtype=np.float64)
vol_ratio = vol_arr / np.maximum(vol_ma, 1.0)

features = np.column_stack([atr_pct, ret_mag, vol_ratio])
valid_mask = np.all(np.isfinite(features), axis=1) & (np.arange(n) >= max(atr_len, ret_len, vol_len))
valid_idx = np.where(valid_mask)[0]

cluster_labels = np.full(n, -1, dtype=np.int32)
n_clusters_found = 0
cluster_centers = None

if len(valid_idx) > min_samples * 3:
    scaler = StandardScaler()
    X = scaler.fit_transform(features[valid_idx])

    db = DBSCAN(eps=eps_val, min_samples=min_samples)
    db.fit(X)
    raw_labels = db.labels_

    unique_labels = set(raw_labels)
    unique_labels.discard(-1)
    n_clusters_found = len(unique_labels)

    # Sort clusters by mean ATR% (ascending: 0=calm, highest=volatile)
    if n_clusters_found > 0:
        center_vol = {}
        for lbl in unique_labels:
            mask = raw_labels == lbl
            center_vol[lbl] = np.mean(X[mask, 0])  # ATR% feature

        sorted_labels = sorted(center_vol.keys(), key=lambda k: center_vol[k])
        label_map = {}
        for new_lbl, old_lbl in enumerate(sorted_labels):
            label_map[old_lbl] = new_lbl

        # Compute cluster centers in original space
        cluster_centers = np.zeros((n_clusters_found, 3))
        for old_lbl, new_lbl in label_map.items():
            mask = raw_labels == old_lbl
            cluster_centers[new_lbl] = np.mean(features[valid_idx[mask]], axis=0)

        for j, idx in enumerate(valid_idx):
            if raw_labels[j] >= 0:
                cluster_labels[idx] = label_map[raw_labels[j]]

# Smoothing
if smoothing > 1 and n_clusters_found > 0:
    smoothed = cluster_labels.copy()
    for i in range(smoothing, n):
        if cluster_labels[i] >= 0:
            window = cluster_labels[i - smoothing:i + 1]
            valid_w = window[window >= 0]
            if len(valid_w) > 0:
                counts = np.bincount(valid_w, minlength=n_clusters_found)
                smoothed[i] = int(np.argmax(counts))
    cluster_labels = smoothed

cluster_float = np.where(cluster_labels >= 0, cluster_labels.astype(np.float64), np.nan)

# Cluster naming
cluster_names = ["Calm", "Moderate", "Active", "Volatile", "Extreme"]
cluster_colors = ["#26A69A", "#42A5F5", "#FF9800", "#FF7043", "#ef5350"]

plot(cluster_float, title="Cluster", color="#FFFFFF")
plot(atr_pct, title="ATR%", color="#78909C")

for i in range(min(n_clusters_found, len(cluster_names))):
    hline(float(i), title=cluster_names[i], color=cluster_colors[i])

# Background coloring
if n_clusters_found > 0:
    calm_mask = cluster_labels == 0
    bgcolor(calm_mask, color="rgba(38,166,154,0.06)")
    if n_clusters_found > 1:
        volatile_mask = cluster_labels == (n_clusters_found - 1)
        bgcolor(volatile_mask, color="rgba(239,83,80,0.10)")

# Transition markers
if show_labels:
    last_label_bar = -label_cooldown
    prev_cluster = -1
    for i in range(max(atr_len, ret_len, vol_len), n):
        if cluster_labels[i] < 0 or cluster_labels[i] == prev_cluster:
            if cluster_labels[i] >= 0:
                prev_cluster = cluster_labels[i]
            continue
        if (i - last_label_bar) < label_cooldown:
            prev_cluster = cluster_labels[i]
            continue

        c = cluster_labels[i]
        name = cluster_names[c] if c < len(cluster_names) else f"C{c}"
        color = cluster_colors[c] if c < len(cluster_colors) else "#FFFFFF"

        label.new(
            i, float(c) + 0.3, name,
            style=label.style_label_down,
            color=color,
            textcolor="#FFFFFF",
            size="small"
        )
        last_label_bar = i
        prev_cluster = cluster_labels[i]

# Centroid info boxes
if show_levels and cluster_centers is not None:
    for c in range(min(n_clusters_found, len(cluster_names))):
        name = cluster_names[c] if c < len(cluster_names) else f"C{c}"
        color = cluster_colors[c] if c < len(cluster_colors) else "#FFFFFF"
        atr_val = float(cluster_centers[c, 0])
        ret_val = float(cluster_centers[c, 1])
        vol_val = float(cluster_centers[c, 2])
        label.new(
            n - 30, float(c) + 0.35,
            f"{name}: ATR%={atr_val:.1f} Ret={ret_val:.1f} Vol={vol_val:.1f}",
            style=label.style_none,
            color=color,
            textcolor=color,
            size="tiny"
        )

# Noise count
noise_count = int(np.sum(cluster_labels == -1))
if noise_count > 0:
    label.new(
        n - 1, float(max(0, n_clusters_found - 1)) + 0.8,
        f"Clusters: {n_clusters_found} | Noise: {noise_count}",
        style=label.style_label_left,
        color="rgba(255,255,255,0.2)",
        textcolor="#888888",
        size="small"
    )
