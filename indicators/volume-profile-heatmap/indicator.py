from tg_scripting import *

length = input.int(50, "Lookback Length", minval=20, maxval=200)
num_levels = input.int(10, "Number of Levels", minval=5, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

import numpy as np

indicator("Volume Profile Heatmap", overlay=True)

hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo
step = rng / num_levels

mid_price = (hi + lo) / 2
vol_at_mid = ta.sma(volume, length)
vol_above = ta.sma(volume * (close > mid_price), length)
vol_below = ta.sma(volume * (close < mid_price), length)

vol_ratio = vol_above / (vol_above + vol_below + 1e-10) * 100

plot(vol_ratio, title="Volume Above/Below Ratio", color="#42A5F5")
plot(ta.sma(vol_ratio, 5), title="Smoothed Ratio", color="#FF7043")
hline(50, title="Equal Distribution", color="rgba(128,128,128,0.4)")
hline(70, title="Volume Skew Up", color="rgba(38,166,154,0.5)")
hline(30, title="Volume Skew Down", color="rgba(239,83,80,0.5)")

plot(mid_price, title="Mid Price", color="#AB47BC")
plot(hi, title="Range High", color="rgba(239,83,80,0.4)")
plot(lo, title="Range Low", color="rgba(38,166,154,0.4)")

bgcolor(vol_ratio > 70, color="rgba(38,166,154,0.06)")
bgcolor(vol_ratio < 30, color="rgba(239,83,80,0.06)")

# --- Rich annotations ---
n = len(close)
last_skew_up_idx = -100
last_skew_down_idx = -100
cooldown_bars = length

for i in range(length + 5, n):
    if show_labels and vol_ratio[i] > 70 and vol_ratio[i - 1] <= 70 and (i - last_skew_up_idx) > cooldown_bars:
        last_skew_up_idx = i
        label.new(
            x=i, y=float(hi[i]),
            text="Vol Skew Up",
            style=label.style_label_down,
            color="rgba(38,166,154,0.25)",
            textcolor="#26a69a",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(mid_price[i]), x2=min(i + length // 2, n - 1), y2=float(mid_price[i]),
                     color="#42a5f5", width=1, style=line.style_dashed)

    if show_labels and vol_ratio[i] < 30 and vol_ratio[i - 1] >= 30 and (i - last_skew_down_idx) > cooldown_bars:
        last_skew_down_idx = i
        label.new(
            x=i, y=float(lo[i]),
            text="Vol Skew Down",
            style=label.style_label_up,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(mid_price[i]), x2=min(i + length // 2, n - 1), y2=float(mid_price[i]),
                     color="#ef5350", width=1, style=line.style_dashed)
