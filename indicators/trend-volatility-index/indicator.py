from tg_scripting import *
import numpy as np

base_length = input.int(5, "Base Length", minval=2, maxval=20)

src = np.array(close, dtype=float)
n = len(src)

# Compute SMAs at multiples of base_length
multipliers = [1, 2, 4, 8]
lengths = [base_length * m for m in multipliers]
smas = []
for l in lengths:
    sma_arr = np.array(ta.sma(src.tolist(), l), dtype=float)
    smas.append(sma_arr)

smas = np.array(smas)  # shape: (4, n)

# Gini mean difference: average absolute difference across all pairs
num_pairs = 0
gmd = np.zeros(n)
for i in range(len(lengths)):
    for j in range(i + 1, len(lengths)):
        gmd += np.abs(smas[i] - smas[j])
        num_pairs += 1

gmd = gmd / num_pairs

# Normalize by price
tvi_raw = gmd / np.where(src > 0, src, 1.0) * 100.0

# Scale to 0-100 using rolling percentile rank
lookback = max(lengths) * 2
tvi = np.zeros(n)
for i in range(lookback, n):
    window = tvi_raw[i - lookback:i + 1]
    rank = float(np.sum(window <= tvi_raw[i])) / float(len(window))
    tvi[i] = rank * 100.0

plot(tvi.tolist(), title="TVI", color=color.purple)
hline(50, title="Midline", color=color.gray)
hline(75, title="Trending", color=color.green)
hline(25, title="Consolidation", color=color.red)
bgcolor(tvi > 75, color="rgba(0,255,0,0.08)")
bgcolor(tvi < 25, color="rgba(255,0,0,0.08)")
