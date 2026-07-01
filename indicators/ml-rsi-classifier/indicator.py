from tg_scripting import *
import numpy as np

indicator("ML RSI Classifier", overlay=False)

# --- Inputs ---
rsi_len = input.int(14, "RSI Length", minval=5, maxval=50)
k_neighbors = input.int(8, "K Neighbors", minval=3, maxval=25)
lookback = input.int(200, "Analog Lookback", minval=50, maxval=500)
feature_window = input.int(5, "Feature Window", minval=3, maxval=20)
confidence_thresh = input.float(0.6, "Confidence Threshold", minval=0.3, maxval=0.95)
show_signals = input.bool(True, "Show Classification Signals")

# --- Compute RSI ---
rsi = ta.rsi(close, rsi_len)
rsi_arr = np.array(rsi, dtype=np.float64)

# --- Feature Engineering Pipeline ---
# 1. RSI Momentum (first derivative)
rsi_momentum = np.diff(rsi_arr, prepend=rsi_arr[0])

# 2. RSI Acceleration (second derivative)
rsi_accel = np.diff(rsi_momentum, prepend=rsi_momentum[0])

# 3. RSI Regime: z-score relative to rolling mean/std
def rolling_zscore(arr, window):
    out = np.full_like(arr, np.nan)
    for i in range(window, len(arr)):
        seg = arr[i - window:i]
        mu, sigma = np.mean(seg), np.std(seg)
        out[i] = (arr[i] - mu) / max(sigma, 1e-10)
    return out

rsi_zscore = rolling_zscore(rsi_arr, feature_window * 4)

# 4. Price-RSI divergence strength via rolling correlation
close_arr = np.array(close, dtype=np.float64)
div_strength = np.full(len(rsi_arr), np.nan)
for i in range(feature_window, len(rsi_arr)):
    seg_price = close_arr[i - feature_window:i]
    seg_rsi = rsi_arr[i - feature_window:i]
    if np.std(seg_price) > 1e-10 and np.std(seg_rsi) > 1e-10:
        div_strength[i] = np.corrcoef(seg_price, seg_rsi)[0, 1]
    else:
        div_strength[i] = 0.0

# 5. Volatility-adjusted RSI: scale by ATR z-score
atr_raw = ta.atr(high, low, close, rsi_len)
atr_arr = np.array(atr_raw, dtype=np.float64)
atr_zscore = rolling_zscore(atr_arr, feature_window * 4)
vol_adj_rsi = rsi_arr * np.where(np.isnan(atr_zscore), 1.0, 1.0 + 0.2 * atr_zscore)

# --- Build Feature Vectors ---
n = len(rsi_arr)
num_features = 5
features = np.column_stack([
    rsi_momentum,
    rsi_accel,
    np.nan_to_num(rsi_zscore, nan=0.0),
    np.nan_to_num(div_strength, nan=0.0),
    np.nan_to_num(vol_adj_rsi, nan=50.0),
])

# --- Forward Return Labels for Historical Analogs ---
fwd_returns = np.roll(close_arr, -feature_window) / close_arr - 1.0
fwd_returns[-feature_window:] = 0.0

# Classification buckets: 0=trending-up, 1=trending-down, 2=ranging, 3=reversal-imminent
price_std = np.full(n, np.nan)
for i in range(feature_window, n):
    price_std[i] = np.std(close_arr[i - feature_window:i]) / max(close_arr[i], 1e-10)
price_std = np.nan_to_num(price_std, nan=0.01)
range_thresh = np.percentile(price_std[feature_window:], 30)

labels = np.full(n, 2, dtype=np.int32)  # default ranging
labels[fwd_returns > 0.005] = 0   # trending-up
labels[fwd_returns < -0.005] = 1  # trending-down
# Reversal-imminent: extreme RSI + opposing next move
reversal_mask = ((rsi_arr > 70) & (fwd_returns < -0.002)) | \
                ((rsi_arr < 30) & (fwd_returns > 0.002))
labels[reversal_mask] = 3

# --- KNN Classification ---
classification = np.full(n, np.nan)
confidence = np.full(n, np.nan)
class_names = {0: 1.0, 1: -1.0, 2: 0.0, 3: 0.5}  # numeric output for plotting

start_idx = max(lookback, feature_window * 4 + 1)
for i in range(start_idx, n):
    current_vec = features[i]
    history_start = max(0, i - lookback)
    history_end = i - feature_window  # avoid look-ahead
    if history_end <= history_start + k_neighbors:
        continue

    history_features = features[history_start:history_end]
    history_labels = labels[history_start:history_end]

    # Vectorized distance computation
    diffs = history_features - current_vec
    distances = np.linalg.norm(diffs, axis=1)

    # Find k nearest neighbors
    nearest_idx = np.argsort(distances)[:k_neighbors]
    nearest_distances = distances[nearest_idx]
    nearest_labels = history_labels[nearest_idx]

    # Inverse-distance weighted voting
    weights = 1.0 / (nearest_distances + 1e-10)
    vote_counts = np.zeros(4)
    for cls in range(4):
        mask = nearest_labels == cls
        vote_counts[cls] = np.sum(weights[mask])

    total_weight = np.sum(vote_counts)
    if total_weight > 0:
        vote_probs = vote_counts / total_weight
        winner = np.argmax(vote_probs)
        classification[i] = class_names[winner]
        confidence[i] = vote_probs[winner]

# --- Apply Confidence Filter ---
filtered_class = np.where(confidence >= confidence_thresh, classification, np.nan)

# --- Signal Arrays ---
trend_up = np.where(filtered_class == 1.0, 1, 0)
trend_down = np.where(filtered_class == -1.0, -1, 0)
reversal_sig = np.where(filtered_class == 0.5, 1, 0)

# --- Plots ---
plot(rsi, title="RSI", color="#7E57C2")
plot(np.nan_to_num(confidence, nan=0.0) * 100, title="Confidence %", color="#26A69A")
hline(70, title="Overbought", color="rgba(255,82,82,0.5)")
hline(30, title="Oversold", color="rgba(76,175,80,0.5)")
hline(confidence_thresh * 100, title="Conf Threshold", color="rgba(255,183,77,0.4)")

if show_signals:
    plotshape(trend_up, title="Trend Up", location="belowbar", style="triangleup", color="#4CAF50")
    plotshape(trend_down, title="Trend Down", location="abovebar", style="triangledown", color="#FF5252")
    plotshape(reversal_sig, title="Reversal Alert", location="abovebar", style="diamond", color="#FF9800")

bgcolor(np.where(filtered_class == 1.0, True, False), color="rgba(76,175,80,0.08)")
bgcolor(np.where(filtered_class == -1.0, True, False), color="rgba(255,82,82,0.08)")
bgcolor(np.where(filtered_class == 0.5, True, False), color="rgba(255,152,0,0.08)")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

last_label_idx = -100
cooldown = 20

for i in range(start_idx, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue
    if np.isnan(filtered_class[i]):
        continue

    if filtered_class[i] == 1.0:
        last_label_idx = i
        label.new(
            x=i, y=float(rsi[i]),
            text="Trend Up",
            style=label.style_label_up,
            color="rgba(76,175,80,0.3)",
            textcolor="#4CAF50",
            size="small"
        )
    elif filtered_class[i] == -1.0:
        last_label_idx = i
        label.new(
            x=i, y=float(rsi[i]),
            text="Trend Down",
            style=label.style_label_down,
            color="rgba(255,82,82,0.3)",
            textcolor="#FF5252",
            size="small"
        )
    elif filtered_class[i] == 0.5:
        last_label_idx = i
        label.new(
            x=i, y=float(rsi[i]),
            text="Reversal",
            style=label.style_label_down,
            color="rgba(255,152,0,0.3)",
            textcolor="#FF9800",
            size="small"
        )

    if show_levels and not np.isnan(confidence[i]):
        label.new(
            x=i, y=float(confidence[i] * 100),
            text=f"{confidence[i]*100:.0f}%",
            style=label.style_none,
            color="rgba(0,0,0,0)",
            textcolor="#26A69A",
            size="tiny"
        )
