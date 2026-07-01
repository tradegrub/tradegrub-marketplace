from tg_scripting import *

indicator("Range Indicator", overlay=False)

length = input.int(14, "Length", minval=2, maxval=100)
pct_len = input.int(100, "Percentile Lookback", minval=20, maxval=500)
high_thresh = input.int(80, "High Range Percentile", minval=60, maxval=95)
low_thresh = input.int(20, "Low Range Percentile", minval=5, maxval=40)

hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo
rng_pct = (rng / close) * 100
rng_percentile = ta.percentrank(rng_pct, pct_len)

plot(rng_pct, title="Range %", color="#42A5F5")
plot(rng_percentile, title="Range Percentile", color="#FF7043")
plot(ta.sma(rng_pct, length), title="Avg Range %", color="#AB47BC")

hline(high_thresh, title="Wide Range", color="rgba(239,83,80,0.5)")
hline(low_thresh, title="Narrow Range", color="rgba(38,166,154,0.5)")

bgcolor(rng_percentile > high_thresh, color="rgba(239,83,80,0.06)")
bgcolor(rng_percentile < low_thresh, color="rgba(38,166,154,0.06)")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

import numpy as np

n = len(close)
last_label_idx = -100
cooldown = 20

for i in range(pct_len, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue

    if i > 0:
        if rng_percentile[i] > high_thresh and rng_percentile[i - 1] <= high_thresh:
            last_label_idx = i
            label.new(
                x=i, y=float(rng_percentile[i]),
                text="Wide Range",
                style=label.style_label_down,
                color="rgba(239,83,80,0.3)",
                textcolor="#ef5350",
                size="small"
            )
            if show_levels:
                label.new(
                    x=i, y=float(rng_pct[i]),
                    text=f"Range: {float(rng_pct[i]):.2f}%",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#ef5350",
                    size="tiny"
                )
        elif rng_percentile[i] < low_thresh and rng_percentile[i - 1] >= low_thresh:
            last_label_idx = i
            label.new(
                x=i, y=float(rng_percentile[i]),
                text="Narrow Range",
                style=label.style_label_up,
                color="rgba(38,166,154,0.3)",
                textcolor="#26a69a",
                size="small"
            )
            if show_levels:
                label.new(
                    x=i, y=float(rng_pct[i]),
                    text=f"Range: {float(rng_pct[i]):.2f}%",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#26a69a",
                    size="tiny"
                )
