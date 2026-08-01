from tg_scripting import *
import numpy as np

lookback = input.int(20, "Lookback", minval=5, maxval=200)

src_vol = np.array(volume, dtype=float)
n = len(src_vol)

# Compute average volume over lookback
avg_vol = np.empty(n, dtype=float)
for i in range(n):
    start = max(0, i - lookback + 1)
    avg_vol[i] = np.mean(src_vol[start:i + 1])

# Volume accumulation profile: for historical bars, compute
# what fraction of the average volume each bar represents at
# various points. Use cumulative volume ratio as completion estimate.
# For each bar, estimate completion rate based on position in the lookback window.
# The last bar is "incomplete" conceptually.

# Build cumulative volume profile using rolling windows
cum_profile = np.empty(n, dtype=float)
for i in range(n):
    start = max(0, i - lookback + 1)
    window = src_vol[start:i + 1]
    window_len = len(window)
    if window_len < 2:
        cum_profile[i] = 1.0
        continue
    # Compute where current bar sits in the cumulative distribution
    cumsum = np.cumsum(window)
    total = cumsum[-1]
    if total > 0:
        # Completion rate: ratio of cumulative volume up to this point
        # relative to what we'd expect
        position = (i - start) / (window_len - 1)  # 0 to 1
        cum_profile[i] = max(0.1, position)  # At least 10% complete
    else:
        cum_profile[i] = 1.0

# For the last bar, project volume
projected_vol = np.where(cum_profile > 0, src_vol / cum_profile, src_vol)

# Projected volume ratio vs average
proj_ratio = np.where(avg_vol > 0, projected_vol / avg_vol, 1.0)

# Clamp extreme values
proj_ratio = np.clip(proj_ratio, 0, 10)

plot(proj_ratio, title="Projected Volume Ratio", color="#42a5f5")
hline(1.0, title="Average", color="#888888")
hline(2.0, title="2x Average", color="#ff9800")
hline(0.5, title="Half Average", color="#ff9800")

bgcolor(proj_ratio > 2.0, color="rgba(66,165,245,0.15)")
bgcolor(proj_ratio < 0.5, color="rgba(255,152,0,0.1)")
