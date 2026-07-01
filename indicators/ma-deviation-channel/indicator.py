from tg_scripting import *
import numpy as np

indicator("MA Deviation Channel", overlay=True)

# Inputs
ma_len = input.int(50, "MA Length", minval=5, maxval=500)
ma_type = input.int(1, "MA Type (1=SMA, 2=EMA)", minval=1, maxval=2)
lookback = input.int(100, "Deviation Lookback", minval=20, maxval=500)
show_extreme = input.bool(True, "Show Extreme Bands")

cl = np.array(close, dtype=float)
n = len(cl)

# Calculate moving average
if ma_type == 1:
    ma_raw = ta.sma(close, ma_len)
else:
    ma_raw = ta.ema(close, ma_len)

ma = np.array(ma_raw, dtype=float)

# Percentage deviation from MA for each bar
dev_pct = np.full(n, np.nan)
valid = ma > 0
dev_pct[valid] = (cl[valid] - ma[valid]) / ma[valid] * 100.0

# Rolling deviation statistics
avg_high = np.full(n, np.nan)
avg_low = np.full(n, np.nan)
ext_high = np.full(n, np.nan)
ext_low = np.full(n, np.nan)

for i in range(lookback, n):
    window = dev_pct[i - lookback:i]
    w_valid = window[~np.isnan(window)]
    if len(w_valid) < 10:
        continue

    pos = w_valid[w_valid > 0]
    neg = w_valid[w_valid < 0]

    avg_high[i] = np.mean(pos) if len(pos) > 0 else 0.0
    avg_low[i] = np.mean(neg) if len(neg) > 0 else 0.0
    ext_high[i] = np.percentile(w_valid, 95) if len(w_valid) > 0 else 0.0
    ext_low[i] = np.percentile(w_valid, 5) if len(w_valid) > 0 else 0.0

# Build channel lines
avg_upper = ma * (1 + avg_high / 100.0)
avg_lower = ma * (1 + avg_low / 100.0)
ext_upper = ma * (1 + ext_high / 100.0)
ext_lower = ma * (1 + ext_low / 100.0)

# Replace NaN with NaN (keep gaps where data is insufficient)
avg_upper[np.isnan(avg_high)] = np.nan
avg_lower[np.isnan(avg_low)] = np.nan
ext_upper[np.isnan(ext_high)] = np.nan
ext_lower[np.isnan(ext_low)] = np.nan

# Plot center MA
p_ma = plot(ma.tolist(), title="MA", color="#2196F3", linewidth=2)

# Plot average deviation bands
p_avg_up = plot(avg_upper.tolist(), title="Avg High Dev", color="#4CAF50", linewidth=1)
p_avg_lo = plot(avg_lower.tolist(), title="Avg Low Dev", color="#F44336", linewidth=1)

# Fill between average bands
fill(p_avg_up, p_ma, color="rgba(76,175,80,0.06)")
fill(p_ma, p_avg_lo, color="rgba(244,67,54,0.06)")

# Plot extreme deviation bands
if show_extreme:
    p_ext_up = plot(ext_upper.tolist(), title="Extreme High Dev", color="#4CAF50", linewidth=1, style="dashed")
    p_ext_lo = plot(ext_lower.tolist(), title="Extreme Low Dev", color="#F44336", linewidth=1, style="dashed")
    fill(p_ext_up, p_avg_up, color="rgba(76,175,80,0.03)")
    fill(p_avg_lo, p_ext_lo, color="rgba(244,67,54,0.03)")
