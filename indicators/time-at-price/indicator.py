from tg_scripting import *
import numpy as np

indicator("Time at Price Levels", overlay=True)

lookback = input.int(200, "Lookback", minval=50, maxval=500)
num_bins = input.int(30, "Number of Bins", minval=10, maxval=100)

src = np.array(close, dtype=float)
n = len(src)

top_levels = []

if n >= lookback:
    segment = src[-lookback:]
    price_min = float(np.min(segment))
    price_max = float(np.max(segment))

    if price_max > price_min:
        bin_edges = np.linspace(price_min, price_max, num_bins + 1)
        bin_counts = np.zeros(num_bins)

        bin_indices = np.digitize(segment, bin_edges) - 1
        bin_indices = np.clip(bin_indices, 0, num_bins - 1)

        for i in range(num_bins):
            bin_counts[i] = float(np.sum(bin_indices == i))

        top_3 = np.argsort(bin_counts)[-3:][::-1]

        for idx in top_3:
            level = (bin_edges[idx] + bin_edges[idx + 1]) / 2.0
            top_levels.append(float(level))

for i, level in enumerate(top_levels):
    colors = ["#FF9800", "#2196F3", "#9C27B0"]
    hline(level, title=f"Dwell Level {i+1}", color=colors[i], linestyle="solid")
