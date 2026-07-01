from tg_scripting import *
import numpy as np
from sklearn.linear_model import SGDClassifier

indicator("Adaptive Trend Detector", overlay=False)

length = input.int(20, "Feature Length", minval=5, maxval=50)
lookback = input.int(80, "Training Lookback", minval=40, maxval=150)
smooth = input.int(5, "Smoothing", minval=1, maxval=15)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

sma_vals = np.array(ta.sma(close, length), dtype=float)
ema_vals = np.array(ta.ema(close, length), dtype=float)
rsi_vals = np.array(ta.rsi(close, length), dtype=float)
atr_vals = np.array(ta.atr(high, low, close, length), dtype=float)

# Price position relative to moving averages
pos_sma = (src - sma_vals) / np.where(atr_vals == 0, 1, atr_vals)
pos_ema = (src - ema_vals) / np.where(atr_vals == 0, 1, atr_vals)
rsi_norm = (rsi_vals - 50) / 50

trend_score = np.full(n, 0.0)
start = lookback + length + 5

for i in range(start, n):
    ts = i - lookback
    X, y = [], []
    for j in range(ts, i - 1):
        X.append([pos_sma[j], pos_ema[j], rsi_norm[j]])
        y.append(1 if src[j + 1] > src[j] else 0)
    X = np.array(X)
    y = np.array(y)
    if len(np.unique(y)) < 2:
        continue
    std = np.std(X, axis=0)
    std[std == 0] = 1
    mu = np.mean(X, axis=0)
    Xn = (X - mu) / std

    clf = SGDClassifier(loss="log_loss", max_iter=100, random_state=42)
    clf.fit(Xn, y)

    xc = np.array([[pos_sma[i], pos_ema[i], rsi_norm[i]]])
    xc_n = (xc - mu) / std
    prob = clf.predict_proba(xc_n)
    if prob.shape[1] == 2:
        trend_score[i] = (prob[0, 1] - 0.5) * 200  # Scale to -100..100

smoothed = np.array(ta.sma(trend_score.tolist(), smooth), dtype=float)


plot(smoothed.tolist(), title="Trend Score", color="#00e5ff", linewidth=2)
plot(trend_score.tolist(), title="Raw Score", color="#42a5f5", linewidth=1)
hline(25, title="Bullish", color="#4CAF50", linestyle="dashed")
hline(-25, title="Bearish", color="#f44336", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
