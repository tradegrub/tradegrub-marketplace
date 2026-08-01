from tg_scripting import *
import numpy as np

lookback = input.int(100, "Lookback", minval=20, maxval=500)
num_bins = input.int(20, "Num Bins", minval=5, maxval=100)

lb = int(lookback)
nb = int(num_bins)

close_arr = np.array(close[:lb], dtype=float)
price_min = np.min(close_arr)
price_max = np.max(close_arr)
price_range = price_max - price_min

if price_range < 1e-10:
    price_range = 1.0

# Create bins and count closes in each
bin_edges = np.linspace(price_min, price_max, nb + 1)
counts, _ = np.histogram(close_arr, bins=bin_edges)

# Find top 3 bins by count
top_indices = np.argsort(counts)[-3:]
top_levels = []
for idx in top_indices:
    mid = (bin_edges[idx] + bin_edges[idx + 1]) / 2.0
    top_levels.append(float(mid))

top_levels.sort()

# Plot the top 3 S/R levels as hlines
colors = [color.green, color.orange, color.red]
titles = ["S/R Level 1", "S/R Level 2", "S/R Level 3"]
for i, level in enumerate(top_levels):
    hline(level, title=titles[i], color=colors[i])
