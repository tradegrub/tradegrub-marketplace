from tg_scripting import *
import numpy as np

indicator("Rolling Autocorrelation Study", overlay=False)

window = input.int(50, "Rolling Window", minval=20, maxval=200)

cl = np.array(close, dtype=float)
n = len(cl)

rets = np.zeros(n)
for i in range(1, n):
    rets[i] = (cl[i] - cl[i-1]) / max(cl[i-1], 1e-10)

lags = [1, 5, 10, 20]
colors = ["#29b6f6", "#66bb6a", "#ff9800", "#ef5350"]
autocorr = {lag: np.zeros(n) for lag in lags}

for i in range(window, n):
    w = rets[i-window:i+1]
    mu = np.mean(w)
    var = np.var(w)
    if var > 1e-20:
        for lag in lags:
            if lag < len(w):
                a = w[lag:] - mu
                b = w[:-lag] - mu
                min_len = min(len(a), len(b))
                autocorr[lag][i] = np.sum(a[:min_len] * b[:min_len]) / (var * len(w))

for idx, lag in enumerate(lags):
    plot(autocorr[lag].tolist(), title=f"AC Lag {lag}", color=colors[idx], linewidth=2 if lag == 1 else 1)

hline(0, title="Zero", color="#888888", linestyle="dashed")
hline(0.2, title="Positive", color="#4CAF50", linestyle="dashed")
hline(-0.2, title="Negative", color="#f44336", linestyle="dashed")

trending = autocorr[1] > 0.2
mean_rev = autocorr[1] < -0.2
bgcolor(trending.tolist(), color="rgba(76,175,80,0.06)")
bgcolor(mean_rev.tolist(), color="rgba(244,67,54,0.06)")
