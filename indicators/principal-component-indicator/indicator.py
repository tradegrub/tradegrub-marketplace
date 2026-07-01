from tg_scripting import *
import numpy as np
from sklearn.decomposition import PCA

indicator("Principal Component Indicator", overlay=False)

length = input.int(14, "Feature Length", minval=5, maxval=50)
lookback = input.int(60, "PCA Window", minval=30, maxval=150)
smooth = input.int(5, "Smoothing", minval=1, maxval=15)

src = np.array(close, dtype=float)
n = len(src)

rsi_vals = np.array(ta.rsi(close, length), dtype=float)
macd_line, macd_sig, macd_hist = ta.macd(close, 12, 26, 9)
macd_h = np.array(macd_hist, dtype=float)
atr_vals = np.array(ta.atr(high, low, close, length), dtype=float)
sma_vals = np.array(ta.sma(close, length), dtype=float)

price_dist = (src - sma_vals) / np.where(atr_vals == 0, 1, atr_vals)
stoch_k, stoch_d = ta.stoch(high, low, close, 14, 3, 3)
stoch_k_arr = np.array(stoch_k, dtype=float)

pc1_score = np.zeros(n)
variance_explained = np.zeros(n)
start = lookback + 30

for i in range(start, n):
    ts = i - lookback
    features = np.column_stack([
        rsi_vals[ts:i + 1],
        macd_h[ts:i + 1],
        price_dist[ts:i + 1],
        stoch_k_arr[ts:i + 1]
    ])
    features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
    mu = np.mean(features, axis=0)
    std = np.std(features, axis=0)
    std[std == 0] = 1
    features_norm = (features - mu) / std

    pca = PCA(n_components=1)
    transformed = pca.fit_transform(features_norm)
    pc1_score[i] = transformed[-1, 0]
    variance_explained[i] = pca.explained_variance_ratio_[0] * 100

# Normalize PC1 to roughly -100 to 100
valid = pc1_score[start:]
if len(valid) > 0:
    std_pc = np.std(valid)
    if std_pc > 0:
        pc1_score = pc1_score / std_pc * 30

smoothed = np.array(ta.sma(pc1_score.tolist(), smooth), dtype=float)


plot(smoothed.tolist(), title="PC1 Factor", color="#26c6da", linewidth=2)
plot(variance_explained.tolist(), title="Variance Explained %", color="#ff9800", linewidth=1)
hline(20, title="Bullish", color="#4CAF50", linestyle="dashed")
hline(-20, title="Bearish", color="#f44336", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
