from tg_scripting import *
import numpy as np

indicator("First Hour Range Predictor", overlay=True)

lookback = input.int(20, "Lookback Period", minval=5, maxval=100)
mult_mid = input.float(1.5, "Mid Target Multiplier", minval=0.5, maxval=5.0, step=0.1)
mult_full = input.float(2.0, "Full Target Multiplier", minval=1.0, maxval=5.0, step=0.1)
show_stops = input.bool(True, "Show Stop Levels")

n = len(close)
first_hour_range = np.zeros(n)
upper_target_mid = np.full(n, np.nan)
upper_target_full = np.full(n, np.nan)
lower_target_mid = np.full(n, np.nan)
lower_target_full = np.full(n, np.nan)
stop_long = np.full(n, np.nan)
stop_short = np.full(n, np.nan)
predicted_range = np.full(n, np.nan)

session_len = 12
for i in range(session_len, n):
    session_start = (i // session_len) * session_len
    if session_start + session_len > n:
        break
    first_bars = min(session_len, 4)
    seg_high = max(high[session_start:session_start + first_bars])
    seg_low = min(low[session_start:session_start + first_bars])
    fhr = seg_high - seg_low
    first_hour_range[i] = fhr

    rolling_ranges = []
    for j in range(max(0, i - lookback), i):
        if first_hour_range[j] > 0:
            rolling_ranges.append(first_hour_range[j])
    avg_range = np.mean(rolling_ranges) if rolling_ranges else fhr

    mid_pt = (seg_high + seg_low) / 2.0
    upper_target_mid[i] = mid_pt + avg_range * mult_mid
    upper_target_full[i] = mid_pt + avg_range * mult_full
    lower_target_mid[i] = mid_pt - avg_range * mult_mid
    lower_target_full[i] = mid_pt - avg_range * mult_full
    stop_long[i] = seg_low
    stop_short[i] = seg_high
    predicted_range[i] = avg_range * mult_full

plot(upper_target_full, title="Upper Full Target", color="#00e676", linewidth=2)
plot(upper_target_mid, title="Upper Mid Target", color="rgba(0,230,118,0.5)", linewidth=1)
plot(lower_target_mid, title="Lower Mid Target", color="rgba(255,82,82,0.5)", linewidth=1)
plot(lower_target_full, title="Lower Full Target", color="#ff5252", linewidth=2)

if show_stops:
    plot(stop_long, title="Long Stop", color="#42a5f5", linewidth=1)
    plot(stop_short, title="Short Stop", color="#ffa726", linewidth=1)
