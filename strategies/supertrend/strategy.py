# Supertrend Strategy
from tg_scripting import *
import numpy as np

indicator("Supertrend", overlay=True)

atr_length = input.int(10, "ATR Length", minval=1, maxval=100)
factor = input.float(3.0, "Factor", minval=0.5, maxval=10.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

supertrend, direction = ta.supertrend(high, low, close, atr_length, factor)

if ta.crossover(direction, 0)[-1]:
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(direction, 0)[-1]:
    strategy.close("Long")

plot(supertrend, title="Supertrend", color="green")

# --- Rich annotations ---
n = len(close)
atr = ta.atr(high, low, close, atr_length)
cross_up = ta.crossover(direction, 0)
cross_down = ta.crossunder(direction, 0)
last_signal_idx = -100

for i in range(atr_length, n):
    if cross_up[i] and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Trend Up",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(supertrend[i])
            tp_price = entry_price + (entry_price - sl_price) * 2
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down[i] and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Trend Down",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
