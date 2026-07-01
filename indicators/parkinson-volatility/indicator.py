from tg_scripting import *
import numpy as np

indicator("Parkinson Volatility", overlay=False)

length = input.int(20, "Length", minval=5, maxval=200)
annual = input.int(252, "Annualization Factor", minval=1, maxval=365)
show_sma = input.bool(True, "Show Smoothed Line")
smooth_len = input.int(10, "Smooth Length", minval=2, maxval=50)

h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
n = len(close)

hl_ratio = np.log(h / np.maximum(l, 1e-10))
hl_sq = hl_ratio ** 2

park_vol = np.full(n, np.nan)
scale = 1.0 / (4.0 * np.log(2.0))

for i in range(length - 1, n):
    window = hl_sq[i - length + 1:i + 1]
    variance = scale * np.mean(window)
    park_vol[i] = np.sqrt(variance * annual) * 100.0

park_sma = np.full(n, np.nan)
if show_sma:
    for i in range(length + smooth_len - 2, n):
        park_sma[i] = np.mean(park_vol[i - smooth_len + 1:i + 1])

high_vol = np.nanpercentile(park_vol[~np.isnan(park_vol)], 80) if np.any(~np.isnan(park_vol)) else 30.0
low_vol = np.nanpercentile(park_vol[~np.isnan(park_vol)], 20) if np.any(~np.isnan(park_vol)) else 10.0

is_high = np.array([False] * n)
is_low = np.array([False] * n)
for i in range(n):
    if not np.isnan(park_vol[i]):
        if park_vol[i] > high_vol:
            is_high[i] = True
        elif park_vol[i] < low_vol:
            is_low[i] = True

plot(park_vol, title="Parkinson Vol", color="#42A5F5", linewidth=2)
if show_sma:
    plot(park_sma, title="Smoothed", color="#FF9800", linewidth=1)
bgcolor(is_high, color="rgba(244,67,54,0.08)")
bgcolor(is_low, color="rgba(76,175,80,0.08)")
hline(high_vol, title="High Vol", color="#EF5350", linestyle="dashed")
hline(low_vol, title="Low Vol", color="#66BB6A", linestyle="dashed")
