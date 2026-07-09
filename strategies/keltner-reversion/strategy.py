# Keltner Channel Mean Reversion
from tg_scripting import *
import numpy as np

indicator("Keltner Reversion", overlay=True)

length = input.int(20, "KC Length", minval=5, maxval=200)
mult = input.float(1.5, "ATR Multiplier", minval=0.5, maxval=5.0)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

upper, basis, lower = ta.kc(close, high, low, close, length, mult)

# Mean reversion entries
n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if ta.crossover(close, lower)[i]:
        strategy.entry("Long", strategy.LONG)

    if ta.crossunder(close, upper)[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit at basis
    if ta.crossover(close, basis)[i]:
        strategy.close("Short")
    if ta.crossunder(close, basis)[i]:
        strategy.close("Long")

plot(upper, title="KC Upper", color="red")
plot(basis, title="KC Basis", color="orange")
plot(lower, title="KC Lower", color="green")
fill("KC Upper", "KC Lower", color="rgba(255, 152, 0, 0.08)")

plotshape(ta.crossover(close, lower), title="Long Entry", shape="triangleup", location="belowbar", color="green")
plotshape(ta.crossunder(close, upper), title="Short Entry", shape="triangledown", location="abovebar", color="red")
plotshape(ta.crossover(close, basis), title="Exit Short", shape="xcross", location="belowbar", color="orange")
plotshape(ta.crossunder(close, basis), title="Exit Long", shape="xcross", location="abovebar", color="orange")

# --- Rich annotations ---
n = len(close)
cross_up_lower = ta.crossover(close, lower)
cross_down_upper = ta.crossunder(close, upper)
last_signal_idx = -100
cooldown = 20

for i in range(length, n):
    if cross_up_lower[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="LONG\nReversion",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            tp_price = float(basis[i])
            sl_price = float(lower[i] - (basis[i] - lower[i]) * 0.5)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="TP (Basis)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down_upper[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="SHORT\nReversion",
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            tp_price = float(basis[i])
            sl_price = float(upper[i] + (upper[i] - basis[i]) * 0.5)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="TP (Basis)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
