from tg_scripting import *
import numpy as np

lookback = input.int(200, "Lookback Period", minval=50, maxval=500)
num_bins = input.int(50, "Number of Bins", minval=10, maxval=200)

# Get price and volume data
h = np.array(high[:lookback], dtype=float)
l = np.array(low[:lookback], dtype=float)
c = np.array(close[:lookback], dtype=float)
v = np.array(volume[:lookback], dtype=float)

# Build volume profile: distribute each bar's volume across its price range
price_min = np.min(l)
price_max = np.max(h)
bin_edges = np.linspace(price_min, price_max, num_bins + 1)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
vol_profile = np.zeros(num_bins)

for i in range(len(h)):
    bar_low = l[i]
    bar_high = h[i]
    mask = (bin_centers >= bar_low) & (bin_centers <= bar_high)
    count = np.sum(mask)
    if count > 0:
        vol_profile[mask] += v[i] / count

# Find local maxima (peaks) with prominence
# A peak is a bin higher than its neighbors
peaks = []
for i in range(1, num_bins - 1):
    if vol_profile[i] > vol_profile[i - 1] and vol_profile[i] > vol_profile[i + 1]:
        # Compute prominence: height above the higher of the two nearest valleys
        left_min = np.min(vol_profile[:i]) if i > 0 else 0
        right_min = np.min(vol_profile[i + 1:]) if i < num_bins - 1 else 0
        prominence = vol_profile[i] - max(left_min, right_min)
        peaks.append((i, prominence, bin_centers[i]))

# Sort by prominence descending, take top 3
peaks.sort(key=lambda x: -x[1])
top_peaks = peaks[:3]

colors = ["#FF6600", "#00AAFF", "#AAFF00"]
for idx, (_, prom, price_level) in enumerate(top_peaks):
    hline(float(price_level), title=f"Volume Node {idx + 1}", color=colors[idx])
