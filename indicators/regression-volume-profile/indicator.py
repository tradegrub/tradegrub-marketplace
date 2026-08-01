from tg_scripting import *
import numpy as np

indicator("Regression Volume Profile", overlay=True)

lookback = input.int(100, "Lookback", minval=20, maxval=500)
degree = input.int(2, "Polynomial Degree", minval=1, maxval=5)
num_bins = input.int(20, "Number of Bins", minval=5, maxval=50)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

reg_line = np.full(n, np.nan)
top_levels = []

if n >= lookback:
    start = n - lookback
    segment = src[start:]
    v_segment = vol[start:]
    x = np.arange(lookback)

    coeffs = np.polyfit(x, segment, degree)
    fitted = np.polyval(coeffs, x)
    reg_line[start:] = fitted

    residuals = segment - fitted

    bin_edges = np.linspace(np.min(residuals), np.max(residuals), num_bins + 1)
    bin_volumes = np.zeros(num_bins)

    bin_indices = np.digitize(residuals, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, num_bins - 1)

    for i in range(num_bins):
        mask = bin_indices == i
        bin_volumes[i] = np.sum(v_segment[mask])

    top_bin_indices = np.argsort(bin_volumes)[-3:][::-1]

    current_reg_val = float(fitted[-1])
    for idx in top_bin_indices:
        bin_center = (bin_edges[idx] + bin_edges[idx + 1]) / 2.0
        level = current_reg_val + bin_center
        top_levels.append(level)

plot(reg_line.tolist(), title="Regression Line", color="#2196F3", linewidth=2)

for i, level in enumerate(top_levels):
    hline(level, title=f"Volume Level {i+1}", color="#FF9800", linestyle="dashed")
