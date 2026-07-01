# Bollinger Bands Strategy
from tg_scripting import *
import numpy as np

indicator("Bollinger Bands", overlay=True)

length = input.int(20, "Length", minval=5, maxval=200)
mult = input.float(2.0, "Std Dev Multiplier", minval=0.5, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

upper, basis, lower = ta.bb(close, length, mult)

if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(close, upper)[-1]:
    strategy.close("Long")

plot(upper, title="Upper Band", color="red")
plot(basis, title="Basis", color="gray")
plot(lower, title="Lower Band", color="green")

# --- Rich annotations ---
cross_up = ta.crossover(close, lower)
cross_down = ta.crossunder(close, upper)
atr = ta.atr(high, low, close, 14)
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30

for i in range(1, n):
    if cross_up[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG\nLower Band",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(lower[i] - atr[i] * 0.5)
            tp_price = float(upper[i])
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="TP (Upper Band)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="EXIT\nUpper Band",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
