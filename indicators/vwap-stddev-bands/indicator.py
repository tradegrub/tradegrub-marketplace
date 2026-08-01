from tg_scripting import *

indicator("VWAP Stddev Bands", overlay=True)

length = input.int(14, "Length", minval=1, maxval=200)
mult = input.float(2.0, "StdDev Multiplier", minval=0.5, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

vwap_val = ta.vwap(high, low, close, volume)
basis = ta.sma(close, length)
dev = mult * ta.stdev(close, length)

upper = vwap_val + dev
lower = vwap_val - dev

plot(vwap_val, title="VWAP", color="blue")
plot(upper, title="Upper Band", color="rgba(38,166,154,0.5)")
plot(lower, title="Lower Band", color="rgba(239,83,80,0.5)")
fill(upper, lower, color="rgba(38,166,154,0.08)")

# --- Rich annotations ---
import numpy as np
n = len(close)
last_upper_touch_idx = -100
last_lower_touch_idx = -100
last_vwap_cross_idx = -100
cooldown_bars = length * 2

for i in range(length + 1, n):
    # Upper band touch (overbought)
    if show_labels and float(high[i]) >= float(upper[i]) and (i - last_upper_touch_idx) > cooldown_bars:
        last_upper_touch_idx = i
        label.new(
            x=i, y=float(upper[i]),
            text="Overbought",
            style=label.style_label_down,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(upper[i]), x2=min(i + length, n - 1), y2=float(upper[i]),
                     color="#ef5350", width=1, style=line.style_dashed)

    # Lower band touch (oversold)
    if show_labels and float(low[i]) <= float(lower[i]) and (i - last_lower_touch_idx) > cooldown_bars:
        last_lower_touch_idx = i
        label.new(
            x=i, y=float(lower[i]),
            text="Oversold",
            style=label.style_label_up,
            color="rgba(0,230,118,0.25)",
            textcolor="#00e676",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(lower[i]), x2=min(i + length, n - 1), y2=float(lower[i]),
                     color="#00e676", width=1, style=line.style_dashed)

    # VWAP crossover
    if show_labels and i > 0 and (i - last_vwap_cross_idx) > cooldown_bars:
        if float(close[i]) > float(vwap_val[i]) and float(close[i - 1]) <= float(vwap_val[i - 1]):
            last_vwap_cross_idx = i
            label.new(
                x=i, y=float(vwap_val[i]),
                text="VWAP Cross Up",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="tiny"
            )
        elif float(close[i]) < float(vwap_val[i]) and float(close[i - 1]) >= float(vwap_val[i - 1]):
            last_vwap_cross_idx = i
            label.new(
                x=i, y=float(vwap_val[i]),
                text="VWAP Cross Down",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#888888",
                size="tiny"
            )
