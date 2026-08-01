from tg_scripting import *
import numpy as np

indicator("Smart Money Concepts", overlay=True)

swing_length = input.int(5, "Swing Length", minval=2, maxval=20)
show_bos = input.bool(True, "Show Break of Structure")
show_fvg = input.bool(True, "Show Fair Value Gaps")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

swing_high = ta.highest(high, swing_length)
swing_low = ta.lowest(low, swing_length)

prev_high = swing_high[swing_length]
prev_low = swing_low[swing_length]

if show_bos:
    bos_up = ta.crossover(close, prev_high)
    bos_down = ta.crossunder(close, prev_low)
    plotshape(bos_up, title="BOS Up", shape="triangleup", location="abovebar", color="green", size="small")
    plotshape(bos_down, title="BOS Down", shape="triangledown", location="belowbar", color="red", size="small")

if show_fvg:
    fvg_bull = low > high[2]
    fvg_bear = high < low[2]
    bgcolor(fvg_bull, color="rgba(38,166,154,0.1)")
    bgcolor(fvg_bear, color="rgba(239,83,80,0.1)")

plot(swing_high, title="Swing High", color="rgba(38,166,154,0.4)", linewidth=1)
plot(swing_low, title="Swing Low", color="rgba(239,83,80,0.4)", linewidth=1)

# --- Rich annotations ---
n = len(close)
last_bos_up_idx = -100
last_bos_down_idx = -100
last_fvg_bull_idx = -100
last_fvg_bear_idx = -100
cooldown = max(swing_length * 4, 20)

for i in range(swing_length + 2, n):
    if show_bos:
        if show_labels and bos_up[i] and (i - last_bos_up_idx) > cooldown:
            last_bos_up_idx = i
            label.new(
                x=i, y=float(high[i]),
                text="BOS Up",
                style=label.style_label_down,
                color="rgba(0,230,118,0.25)",
                textcolor="#00e676",
                size="small"
            )
            if show_levels:
                line.new(x1=i - swing_length, y1=float(swing_high[i]), x2=i, y2=float(swing_high[i]),
                         color="#00e676", width=1, style=line.style_dashed)

        if show_labels and bos_down[i] and (i - last_bos_down_idx) > cooldown:
            last_bos_down_idx = i
            label.new(
                x=i, y=float(low[i]),
                text="BOS Down",
                style=label.style_label_up,
                color="rgba(239,83,80,0.25)",
                textcolor="#ef5350",
                size="small"
            )
            if show_levels:
                line.new(x1=i - swing_length, y1=float(swing_low[i]), x2=i, y2=float(swing_low[i]),
                         color="#ef5350", width=1, style=line.style_dashed)

    if show_fvg:
        if show_labels and i >= 2 and fvg_bull[i] and (i - last_fvg_bull_idx) > cooldown:
            last_fvg_bull_idx = i
            label.new(
                x=i - 1, y=float(low[i]),
                text="FVG",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#26a69a",
                size="tiny"
            )
            if show_levels:
                box.new(left=i - 2, top=float(low[i]), right=i, bottom=float(high[i - 2]),
                        border_color="rgba(38,166,154,0.3)", bgcolor="rgba(38,166,154,0.05)")

        if show_labels and i >= 2 and fvg_bear[i] and (i - last_fvg_bear_idx) > cooldown:
            last_fvg_bear_idx = i
            label.new(
                x=i - 1, y=float(high[i]),
                text="FVG",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#ef5350",
                size="tiny"
            )
            if show_levels:
                box.new(left=i - 2, top=float(low[i - 2]), right=i, bottom=float(high[i]),
                        border_color="rgba(239,83,80,0.3)", bgcolor="rgba(239,83,80,0.05)")
