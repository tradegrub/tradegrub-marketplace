from tg_scripting import *
import numpy as np

indicator("Hurst Cycle Pivots", overlay=False)

lookback = input.int(50, "Lookback", minval=20, maxval=200)
rs_periods = input.int(20, "R/S Periods", minval=5, maxval=50)

src = np.array(close, dtype=float)
n = len(src)

def rescaled_range(data):
    """Compute R/S statistic for a series."""
    mean = np.mean(data)
    deviations = np.cumsum(data - mean)
    r = np.max(deviations) - np.min(deviations)
    s = np.std(data, ddof=1)
    if s < 1e-10:
        return 0.0
    return r / s

hurst = np.full(n, np.nan)

for i in range(lookback, n):
    window = src[i - lookback:i]
    log_returns = np.diff(np.log(window))

    # R/S analysis across multiple sub-period sizes
    sizes = []
    rs_values = []
    max_size = len(log_returns) // 2
    size = rs_periods
    while size <= max_size and size >= 4:
        num_blocks = len(log_returns) // size
        if num_blocks < 1:
            size += rs_periods
            continue
        rs_sum = 0.0
        count = 0
        for j in range(num_blocks):
            block = log_returns[j * size:(j + 1) * size]
            rs_val = rescaled_range(block)
            if rs_val > 0:
                rs_sum += np.log(rs_val)
                count += 1
        if count > 0:
            sizes.append(np.log(size))
            rs_values.append(rs_sum / count)
        size += rs_periods

    if len(sizes) >= 2:
        # Linear regression: log(R/S) = H * log(n) + c
        sizes_arr = np.array(sizes)
        rs_arr = np.array(rs_values)
        slope = np.polyfit(sizes_arr, rs_arr, 1)[0]
        hurst[i] = np.clip(slope, 0.0, 1.0)

# Detect mean-reversion pivots: Hurst drops below 0.5
pivot_points = np.zeros(n, dtype=bool)
for i in range(1, n):
    if not np.isnan(hurst[i]) and not np.isnan(hurst[i - 1]):
        if hurst[i] < 0.5 and hurst[i - 1] >= 0.5:
            pivot_points[i] = True

plot(hurst.tolist(), title="Hurst Exponent", color="#26c6da", linewidth=2)
hline(0.5, title="Random Walk", color="#ff9800", linestyle="dashed")
hline(1.0, title="Trending", color="#66bb6a", linestyle="dotted")
hline(0.0, title="Mean Reverting", color="#ef5350", linestyle="dotted")
plotshape(pivot_points.tolist(), title="Cycle Pivot", style="diamond", location="belowbar", color="#ffeb3b", size="small")
bgcolor((hurst < 0.5).tolist(), color="rgba(239,83,80,0.1)")
