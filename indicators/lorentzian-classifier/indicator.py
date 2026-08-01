from tg_scripting import *
import numpy as np


lookback = input.int(100, "Lookback", minval=20, maxval=500)
neighbors = input.int(8, "Neighbors", minval=3, maxval=50)

h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

# --- Feature 1: RSI ---
rsi_len = 14
rsi_vals = np.array(ta.rsi(close, rsi_len), dtype=float)

# --- Feature 2: CCI ---
cci_len = 20
cci_vals = np.array(ta.cci(close, cci_len), dtype=float)

# --- Feature 3: ADX proxy (smoothed directional movement ratio) ---
adx_len = 14
plus_dm = np.zeros(n)
minus_dm = np.zeros(n)
tr = np.zeros(n)
for i in range(1, n):
    up_move = h[i] - h[i - 1]
    down_move = l[i - 1] - l[i]
    plus_dm[i] = up_move if (up_move > down_move) & (up_move > 0) else 0.0
    minus_dm[i] = down_move if (down_move > up_move) & (down_move > 0) else 0.0
    tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))

smooth_tr = np.full(n, np.nan)
smooth_pdm = np.full(n, np.nan)
smooth_mdm = np.full(n, np.nan)
adx_proxy = np.full(n, np.nan)

if n > adx_len:
    smooth_tr[adx_len] = np.sum(tr[1:adx_len + 1])
    smooth_pdm[adx_len] = np.sum(plus_dm[1:adx_len + 1])
    smooth_mdm[adx_len] = np.sum(minus_dm[1:adx_len + 1])
    for i in range(adx_len + 1, n):
        smooth_tr[i] = smooth_tr[i - 1] - (smooth_tr[i - 1] / adx_len) + tr[i]
        smooth_pdm[i] = smooth_pdm[i - 1] - (smooth_pdm[i - 1] / adx_len) + plus_dm[i]
        smooth_mdm[i] = smooth_mdm[i - 1] - (smooth_mdm[i - 1] / adx_len) + minus_dm[i]
    for i in range(adx_len, n):
        if smooth_tr[i] > 0:
            pdi = 100.0 * smooth_pdm[i] / smooth_tr[i]
            mdi = 100.0 * smooth_mdm[i] / smooth_tr[i]
            dsum = pdi + mdi
            adx_proxy[i] = 100.0 * abs(pdi - mdi) / dsum if dsum > 0 else 0.0
        else:
            adx_proxy[i] = 0.0

# --- Feature 4: ROC (Rate of Change) ---
roc_len = 10
roc_vals = np.full(n, np.nan)
for i in range(roc_len, n):
    if c[i - roc_len] != 0:
        roc_vals[i] = ((c[i] - c[i - roc_len]) / c[i - roc_len]) * 100.0

# --- Feature 5: Volatility Ratio (ATR / close) ---
atr_vals = np.array(ta.atr(high, low, close, 14), dtype=float)
vol_ratio = np.full(n, np.nan)
for i in range(n):
    if c[i] > 0 and not np.isnan(atr_vals[i]):
        vol_ratio[i] = (atr_vals[i] / c[i]) * 100.0

# --- Stack features and normalize ---
features = np.column_stack([rsi_vals, cci_vals, adx_proxy, roc_vals, vol_ratio])

feat_mean = np.nanmean(features, axis=0)
feat_std = np.nanstd(features, axis=0)
feat_std[feat_std == 0] = 1.0
norm_features = (features - feat_mean) / feat_std

# --- KNN classification using Lorentzian distance ---
score = np.full(n, np.nan)
min_start = max(lookback, 30)

for i in range(min_start, n):
    fi = norm_features[i]
    if np.any(np.isnan(fi)):
        continue

    start_idx = max(0, i - lookback)
    distances = []

    for j in range(start_idx, i - 1):
        fj = norm_features[j]
        if np.any(np.isnan(fj)):
            continue
        d = np.sum(np.log(1.0 + np.abs(fi - fj)))
        future_ret = c[j + 1] - c[j] if j + 1 < n else 0.0
        distances.append((d, future_ret))

    if len(distances) < neighbors:
        continue

    distances.sort(key=lambda x: x[0])
    top_k = distances[:neighbors]

    bullish = sum(1 for _, ret in top_k if ret > 0)
    bearish = sum(1 for _, ret in top_k if ret < 0)
    total = bullish + bearish
    if total > 0:
        score[i] = ((bullish - bearish) / total) * 100.0
    else:
        score[i] = 0.0

# --- Plotting ---
is_bullish = np.array([not np.isnan(score[i]) and score[i] > 50 for i in range(n)])
is_bearish = np.array([not np.isnan(score[i]) and score[i] < -50 for i in range(n)])

plot(score, title="Classification Score", color="#26C6DA")
hline(50.0, title="Strong Bullish", color="#4CAF50")
hline(-50.0, title="Strong Bearish", color="#EF5350")
hline(0.0, title="Neutral", color="#888888")
bgcolor(is_bullish, color="rgba(76,175,80,0.08)")
bgcolor(is_bearish, color="rgba(244,67,54,0.08)")
