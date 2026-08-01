from tg_scripting import *

indicator("Zscore Indicator", overlay=False)

length = input.int(20, "Length", minval=5, maxval=200)
ob_level = input.float(2.0, "Overbought Z-Score", minval=0.5, maxval=4.0)
os_level = input.float(-2.0, "Oversold Z-Score", minval=-4.0, maxval=-0.5)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

sma_val = ta.sma(close, length)
stdev_val = ta.stdev(close, length)
zscore = (close - sma_val) / stdev_val

plot(zscore, title="Z-Score", color="#7E57C2")
h_ob = hline(ob_level, title="Overbought", color="rgba(239,83,80,0.5)")
h_os = hline(os_level, title="Oversold", color="rgba(38,166,154,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.4)")
fill(h_ob, h_os, color="rgba(126,87,194,0.05)")

bgcolor(zscore > ob_level, color="rgba(239,83,80,0.08)")
bgcolor(zscore < os_level, color="rgba(38,166,154,0.08)")

# --- Rich annotations ---
import numpy as np
n = len(close)
last_ob_idx = -100
last_os_idx = -100
last_zero_cross_idx = -100
cooldown_bars = length

for i in range(length + 1, n):
    # Overbought entry
    if show_labels and zscore[i] > ob_level and zscore[i - 1] <= ob_level and (i - last_ob_idx) > cooldown_bars:
        last_ob_idx = i
        label.new(
            x=i, y=float(zscore[i]),
            text="Overbought",
            style=label.style_label_down,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(ob_level), x2=min(i + length, n - 1), y2=float(ob_level),
                     color="#ef5350", width=1, style=line.style_dotted)

    # Oversold entry
    if show_labels and zscore[i] < os_level and zscore[i - 1] >= os_level and (i - last_os_idx) > cooldown_bars:
        last_os_idx = i
        label.new(
            x=i, y=float(zscore[i]),
            text="Oversold",
            style=label.style_label_up,
            color="rgba(0,230,118,0.25)",
            textcolor="#00e676",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(os_level), x2=min(i + length, n - 1), y2=float(os_level),
                     color="#00e676", width=1, style=line.style_dotted)

    # Zero line cross
    if show_labels and i > 0 and (i - last_zero_cross_idx) > cooldown_bars:
        if zscore[i] > 0 and zscore[i - 1] <= 0:
            last_zero_cross_idx = i
            label.new(
                x=i, y=0.0,
                text="Cross Up",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="tiny"
            )
        elif zscore[i] < 0 and zscore[i - 1] >= 0:
            last_zero_cross_idx = i
            label.new(
                x=i, y=0.0,
                text="Cross Down",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#888888",
                size="tiny"
            )
