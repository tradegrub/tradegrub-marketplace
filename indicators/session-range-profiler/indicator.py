from tg_scripting import *
import numpy as np

indicator("Session Range Profiler", overlay=False)

session_len = input.int(20, "Session Length", minval=5, maxval=100)
show_direction = input.bool(True, "Show Direction Bias")

src_h = np.array(high, dtype=float)
src_l = np.array(low, dtype=float)
src_c = np.array(close, dtype=float)
src_o = np.array(open, dtype=float)
src_v = np.array(volume, dtype=float)
n = len(src_c)

sess_range = np.full(n, np.nan)
avg_range = np.full(n, np.nan)
direction = np.full(n, 0.0)
vol_intensity = np.full(n, np.nan)

for i in range(session_len, n):
    seg_h = src_h[i - session_len:i]
    seg_l = src_l[i - session_len:i]
    seg_c = src_c[i - session_len:i]
    seg_o = src_o[i - session_len:i]
    seg_v = src_v[i - session_len:i]

    bar_ranges = seg_h - seg_l
    sess_range[i] = np.sum(bar_ranges)

    if i >= session_len * 3:
        past_ranges = []
        for j in range(1, 4):
            start = i - session_len * j - session_len
            end = i - session_len * j
            if start >= 0:
                past_ranges.append(np.sum(src_h[start:end] - src_l[start:end]))
        if past_ranges:
            avg_range[i] = np.mean(past_ranges)

    up_vol = np.sum(seg_v[seg_c > seg_o])
    dn_vol = np.sum(seg_v[seg_c < seg_o])
    total_vol = up_vol + dn_vol
    if total_vol > 0:
        direction[i] = (up_vol - dn_vol) / total_vol

    vol_intensity[i] = np.mean(seg_v)

is_bullish = direction > 0.1
is_bearish = direction < -0.1

plot(sess_range, title="Session Range", color="#42A5F5", linewidth=2)
plot(avg_range, title="Avg Range", color="#FFA726", linewidth=1)
plot(vol_intensity, title="Volume Intensity", color="rgba(171,71,188,0.5)", linewidth=1)

if show_direction:
    bgcolor(is_bullish, color="rgba(76,175,80,0.08)")
    bgcolor(is_bearish, color="rgba(239,83,80,0.08)")

hline(0, title="Zero", color="#555", linestyle="dashed")
