# Bollinger Band Width Squeeze Expansion
from tg_scripting import *
import numpy as np

indicator("BB Width Squeeze", overlay=True)

bb_length = input.int(20, "BB Length", minval=5, maxval=200)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=5.0)
squeeze_pct = input.float(0.02, "Squeeze Threshold", minval=0.005, maxval=0.1)
lookback = input.int(50, "Width Lookback", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

upper, basis, lower = ta.bb(close, bb_length, bb_mult)
bb_width = ta.bbw(close, bb_length, bb_mult)

# Detect squeeze: width at historical low
width_min = ta.lowest(bb_width, lookback)
is_squeeze = bb_width <= width_min * 1.05

# Expansion breakout after squeeze
n = len(close)
for i in range(2, n):
    strategy.set_bar_index(i)
    expanding_i = bb_width[i] > bb_width[i-1] * 1.1
    if is_squeeze[i-1] and expanding_i:
        if close[i] > basis[i]:
            strategy.entry("Long", strategy.LONG)
        else:
            strategy.entry("Short", strategy.SHORT)
    if ta.crossunder(close, basis)[i]:
        strategy.close("Long")
    if ta.crossover(close, basis)[i]:
        strategy.close("Short")

p_bb_upper = plot(upper, title="Upper Band", color="#9c27b0")
plot(basis, title="Basis", color="#42a5f5")
p_bb_lower = plot(lower, title="Lower Band", color="#9c27b0")
fill(p_bb_upper, p_bb_lower, color="rgba(156,39,176,0.06)")

plot(bb_width, title="BB Width", color="#ff9800")
plot(width_min * 1.05, title="Squeeze Level", color="#ff9800")

bgcolor(is_squeeze, color="rgba(255, 235, 59, 0.12)")

expand_long = np.zeros(n, dtype=bool)
expand_short = np.zeros(n, dtype=bool)
for i in range(2, n):
    _expanding = bb_width[i] > bb_width[i-1] * 1.1
    if is_squeeze[i-1] and _expanding:
        if close[i] > basis[i]:
            expand_long[i] = True
        else:
            expand_short[i] = True

plotshape(expand_long.tolist(), title="Long Expansion", style="triangleup", location="belowbar", color="#00e676")
plotshape(expand_short.tolist(), title="Short Expansion", style="triangledown", location="abovebar", color="#ef5350")

# --- Rich annotations ---
atr = ta.atr(high, low, close, 14)
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30
squeeze_label_placed = False

for i in range(2, n):
    # Label squeeze zones
    if show_labels and is_squeeze[i] and not squeeze_label_placed:
        squeeze_label_placed = True
        label.new(x=i, y=float(high[i]), text="Squeeze",
                  style=label.style_label_down, color="rgba(255,235,59,0.4)",
                  textcolor="#fdd835", size="normal")

    # Reset squeeze label when squeeze ends
    if not is_squeeze[i]:
        squeeze_label_placed = False

    # Expansion breakout signal
    expanding_i = bb_width[i] > bb_width[i - 1] * 1.1
    if is_squeeze[i - 1] and expanding_i and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if close[i] > basis[i]:
            if show_labels:
                label.new(x=i, y=float(low[i]), text="LONG\nExpansion",
                          style=label.style_label_up, color="#00e676",
                          textcolor="#000000", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(lower[i])
                tp_price = float(upper[i])
                end_bar = min(i + exit_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=entry_price, text="Entry",
                          style=label.style_label_left, color="rgba(66,165,245,0.2)",
                          textcolor="#42a5f5", size="small")
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop (Lower BB)",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="TP (Upper BB)",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                        border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")
        else:
            if show_labels:
                label.new(x=i, y=float(high[i]), text="SHORT\nExpansion",
                          style=label.style_label_down, color="#ef5350",
                          textcolor="#ffffff", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(upper[i])
                tp_price = float(lower[i])
                end_bar = min(i + exit_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop (Upper BB)",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="TP (Lower BB)",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                        border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
