from tg_scripting import *
import numpy as np

indicator("Normalized Volume Volatility", overlay=False)

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
num_sigma = input.float(1.0, "Sigma Threshold", minval=0.5, maxval=3.0, step=0.5)
show_volatility = input.bool(True, "Show Volatility")
show_regression = input.bool(True, "Show Regression")

vol = np.array(volume, dtype=float)
n = len(vol)

# --- Normalized Volume ---
norm_vol = np.full(n, np.nan)
for i in range(lookback, n):
    window = vol[i - lookback:i]
    mean_v = np.mean(window)
    std_v = np.std(window)
    baseline = mean_v + num_sigma * std_v
    if baseline > 0:
        norm_vol[i] = (vol[i] / baseline) * 100

# --- ATR (volatility) ---
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)

tr = np.zeros(n)
tr[0] = hi[0] - lo[0]
for i in range(1, n):
    tr[i] = max(hi[i] - lo[i], abs(hi[i] - cl[i - 1]), abs(lo[i] - cl[i - 1]))

atr = np.zeros(n)
atr[:lookback] = np.nan
if lookback <= n:
    atr[lookback - 1] = np.mean(tr[:lookback])
    alpha = 1.0 / lookback
    for i in range(lookback, n):
        atr[i] = alpha * tr[i] + (1 - alpha) * atr[i - 1]

# --- Normalized Volatility ---
norm_atr = np.full(n, np.nan)
for i in range(lookback * 2, n):
    window = atr[i - lookback:i]
    mean_a = np.mean(window)
    std_a = np.std(window)
    baseline = mean_a + num_sigma * std_a
    if baseline > 0:
        norm_atr[i] = (atr[i] / baseline) * 100

# --- Linear Regression on Normalized Volume ---
reg_line = np.full(n, np.nan)
if show_regression:
    valid = ~np.isnan(norm_vol)
    idx = np.where(valid)[0]
    if len(idx) >= 2:
        coeffs = np.polyfit(idx, norm_vol[idx], 1)
        reg_line[idx] = np.polyval(coeffs, idx)

# --- Volume bar colors ---
vol_colors = []
for i in range(n):
    if np.isnan(norm_vol[i]):
        vol_colors.append("#888888")
    elif norm_vol[i] >= 100:
        vol_colors.append("#4CAF50")
    else:
        vol_colors.append("#f44336")

# --- Plot ---
plot(norm_vol.tolist(), title="Norm Volume", style="histogram", color=vol_colors, linewidth=2)

if show_volatility:
    plot(norm_atr.tolist(), title="Norm Volatility", color="#ff9800", linewidth=2)

if show_regression:
    plot(reg_line.tolist(), title="Vol Regression", color="#42a5f5", linewidth=1, linestyle="dashed")

hline(100, title="Normal Level", color="#ffffff", linestyle="dashed")
