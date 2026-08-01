from tg_scripting import *
import numpy as np

indicator("MESA Adaptive Stochastic", overlay=False)

min_period = input.int(5, "Min Period", minval=2, maxval=20)
max_period = input.int(50, "Max Period", minval=20, maxval=100)
d_smooth = input.int(3, "D Smoothing", minval=1, maxval=10)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

# MESA autocorrelation cycle detection
dominant_period = np.full(n, float(min_period + max_period) / 2.0)

for i in range(max_period * 2, n):
    window = cl[i - max_period * 2:i]
    window = window - np.mean(window)

    # Autocorrelation for each candidate period
    best_period = min_period
    best_corr = -1.0
    for p in range(min_period, max_period + 1):
        if len(window) < p * 2:
            continue
        seg1 = window[-p:]
        seg2 = window[-2 * p:-p]
        denom = np.sqrt(np.sum(seg1 ** 2) * np.sum(seg2 ** 2))
        if denom > 0:
            corr = np.sum(seg1 * seg2) / denom
            if corr > best_corr:
                best_corr = corr
                best_period = p

    dominant_period[i] = float(best_period)

# Smooth the dominant period to avoid jumps
alpha_p = 2.0 / (max_period / 2 + 1)
for i in range(1, n):
    dominant_period[i] = alpha_p * dominant_period[i] + (1 - alpha_p) * dominant_period[i - 1]

# Adaptive stochastic: use dominant_period as lookback
k_vals = np.full(n, 50.0)
for i in range(max_period, n):
    lb = max(min_period, min(max_period, int(round(dominant_period[i]))))
    h_max = np.max(hi[i - lb + 1:i + 1])
    l_min = np.min(lo[i - lb + 1:i + 1])
    rng = h_max - l_min
    if rng > 0:
        k_vals[i] = (cl[i] - l_min) / rng * 100.0
    else:
        k_vals[i] = 50.0

# %D is SMA of %K
d_vals = np.copy(k_vals)
for i in range(d_smooth, n):
    d_vals[i] = np.mean(k_vals[i - d_smooth + 1:i + 1])

plot(k_vals.tolist(), title="%K", color="#26c6da", linewidth=2)
plot(d_vals.tolist(), title="%D", color="#ff9800", linewidth=1)
hline(80, title="Overbought", color="#f44336", linestyle="dashed")
hline(20, title="Oversold", color="#4CAF50", linestyle="dashed")

ob_zone = k_vals > 80
os_zone = k_vals < 20
bgcolor(ob_zone.tolist(), color="rgba(244,67,54,0.08)")
bgcolor(os_zone.tolist(), color="rgba(76,175,80,0.08)")
