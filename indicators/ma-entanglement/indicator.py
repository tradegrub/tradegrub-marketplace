from tg_scripting import *
import numpy as np

indicator("MA Entanglement Index", overlay=False)

cl = np.array(close, dtype=float)
n = len(cl)

periods = [5, 10, 15, 20, 30, 50]
smas = []
for p in periods:
    arr = np.array(ta.sma(close, p), dtype=float)
    arr = np.nan_to_num(arr, nan=0.0)
    smas.append(arr)

sma_matrix = np.stack(smas, axis=0)

num_pairs = 15
pair_diffs = np.zeros(n)
count = 0
for i in range(len(periods)):
    for j in range(i + 1, len(periods)):
        diff = np.abs(sma_matrix[i] - sma_matrix[j])
        safe_price = np.where(cl > 0, cl, 1.0)
        pair_diffs += diff / safe_price
        count += 1

raw_entangle = pair_diffs / count * 100

lookback = 100
entangle_norm = np.zeros(n)
for i in range(lookback, n):
    window = raw_entangle[i - lookback:i + 1]
    mn = np.min(window)
    mx = np.max(window)
    if mx > mn:
        entangle_norm[i] = (raw_entangle[i] - mn) / (mx - mn) * 100

smoothed = np.copy(entangle_norm)
alpha = 2.0 / (6)
for i in range(1, n):
    smoothed[i] = alpha * entangle_norm[i] + (1 - alpha) * smoothed[i - 1]

consolidation = smoothed < 20
trending = smoothed > 60

plot(smoothed.tolist(), title="Entanglement Index", color="#ab47bc", linewidth=2)
hline(20, title="Consolidation", color="#4CAF50", linestyle="dashed")
hline(50, title="Midline", color="#888888", linestyle="dashed")
hline(80, title="Strong Trend", color="#f44336", linestyle="dashed")
bgcolor(consolidation.tolist(), color="rgba(76,175,80,0.06)")
bgcolor(trending.tolist(), color="rgba(244,67,54,0.06)")
