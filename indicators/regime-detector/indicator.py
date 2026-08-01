from tg_scripting import *
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

indicator("Market Regime Detector", overlay=False)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
ret_len = input.int(10, "Returns Lookback", minval=3, maxval=50)
vol_len = input.int(20, "Volume MA Length", minval=5, maxval=100)
n_clusters = input.int(3, "Number of Regimes", minval=2, maxval=5)
smoothing = input.int(3, "Regime Smoothing", minval=1, maxval=10)
label_cooldown = input.int(15, "Label Cooldown Bars", minval=5, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

close_arr = np.array(close, dtype=np.float64)
high_arr = np.array(high, dtype=np.float64)
low_arr = np.array(low, dtype=np.float64)
vol_arr = np.array(volume, dtype=np.float64)
n = len(close_arr)

atr_raw = ta.atr(high, low, close, atr_len)
atr_arr = np.array(atr_raw, dtype=np.float64)
atr_pct = (atr_arr / np.maximum(close_arr, 1e-10)) * 100.0

returns = np.zeros(n)
for i in range(ret_len, n):
    returns[i] = (close_arr[i] / close_arr[i - ret_len] - 1.0) * 100.0

abs_returns = np.abs(returns)

vol_ma = np.array(ta.sma(volume, vol_len), dtype=np.float64)
vol_ratio = vol_arr / np.maximum(vol_ma, 1.0)

def rolling_std(arr, window):
    out = np.zeros(n)
    for i in range(window, n):
        out[i] = np.std(arr[i - window:i])
    return out

ret_volatility = rolling_std(returns, ret_len)

features = np.column_stack([
    atr_pct,
    abs_returns,
    vol_ratio,
    ret_volatility,
])

valid_mask = np.all(np.isfinite(features), axis=1) & (np.arange(n) >= max(atr_len, ret_len, vol_len))
valid_idx = np.where(valid_mask)[0]

regime = np.full(n, -1, dtype=np.int32)
centroids = None

if len(valid_idx) > n_clusters * 10:
    scaler = StandardScaler()
    X = scaler.fit_transform(features[valid_idx])

    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    km.fit(X)
    raw_labels = km.labels_

    center_volatility = km.cluster_centers_[:, 0] + km.cluster_centers_[:, 3]
    order = np.argsort(center_volatility)
    label_map = np.zeros(n_clusters, dtype=np.int32)
    for new_label, old_label in enumerate(order):
        label_map[old_label] = new_label

    for j, idx in enumerate(valid_idx):
        regime[idx] = label_map[raw_labels[j]]

    centroids = km.cluster_centers_[order]

if smoothing > 1:
    smoothed = regime.copy()
    for i in range(smoothing, n):
        if regime[i] >= 0:
            window = regime[i - smoothing:i + 1]
            valid_window = window[window >= 0]
            if len(valid_window) > 0:
                counts = np.bincount(valid_window, minlength=n_clusters)
                smoothed[i] = int(np.argmax(counts))
    regime = smoothed

regime_float = np.where(regime >= 0, regime.astype(np.float64), np.nan)

regime_names = ["Trending", "Ranging", "Volatile"]
if n_clusters == 2:
    regime_names = ["Calm", "Volatile"]
elif n_clusters == 4:
    regime_names = ["Trending", "Ranging", "Active", "Volatile"]
elif n_clusters == 5:
    regime_names = ["Trending", "Calm", "Ranging", "Active", "Volatile"]

regime_colors = ["#26A69A", "#42A5F5", "#FF7043", "#AB47BC", "#FFA726"]

plot(regime_float, title="Regime", color="#FFFFFF")
plot(atr_pct, title="ATR%", color="#78909C")

for i in range(min(n_clusters, len(regime_names))):
    hline(float(i), title=regime_names[i], color=regime_colors[i])

trending_mask = regime == 0
ranging_mask = regime == 1
volatile_mask = regime == (n_clusters - 1)

bgcolor(trending_mask, color="rgba(38,166,154,0.08)")
bgcolor(ranging_mask, color="rgba(66,165,245,0.08)")
bgcolor(volatile_mask, color="rgba(255,112,67,0.12)")

if show_labels:
    last_label_bar = -label_cooldown
    prev_regime = -1
    for i in range(max(atr_len, ret_len, vol_len), n):
        if regime[i] < 0 or regime[i] == prev_regime:
            if regime[i] >= 0:
                prev_regime = regime[i]
            continue
        if (i - last_label_bar) < label_cooldown:
            prev_regime = regime[i]
            continue

        r = regime[i]
        name = regime_names[r] if r < len(regime_names) else f"R{r}"
        color = regime_colors[r] if r < len(regime_colors) else "#FFFFFF"

        label.new(
            i, float(r) + 0.3, name,
            style=label.style_label_down,
            color=color,
            textcolor="#FFFFFF",
            size="small"
        )
        last_label_bar = i
        prev_regime = regime[i]

if show_levels and centroids is not None:
    for c in range(min(n_clusters, len(regime_names))):
        avg_atr = float(centroids[c, 0])
        avg_vol = float(centroids[c, 3])
        name = regime_names[c] if c < len(regime_names) else f"R{c}"
        color = regime_colors[c] if c < len(regime_colors) else "#FFFFFF"
        box.new(
            n - 60, float(c) + 0.4, n - 1, float(c) - 0.1,
            border_color=color,
            bgcolor=color.replace(")", ",0.15)").replace("rgb(", "rgba(") if "rgb" in color else "rgba(128,128,128,0.15)"
        )
        label.new(
            n - 30, float(c) + 0.35,
            f"{name}: ATR%={avg_atr:.1f} Vol={avg_vol:.2f}",
            style=label.style_none,
            color=color,
            textcolor=color,
            size="tiny"
        )
