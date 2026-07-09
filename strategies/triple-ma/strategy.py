# Triple Moving Average Strategy
from tg_scripting import *
import numpy as np

strategy("Triple MA", overlay=True)

fast_len = input.int(10, "Fast SMA", minval=2, maxval=50)
mid_len = input.int(20, "Mid SMA", minval=5, maxval=100)
slow_len = input.int(50, "Slow SMA", minval=20, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

fast_sma = ta.sma(close, fast_len)
mid_sma = ta.sma(close, mid_len)
slow_sma = ta.sma(close, slow_len)

long_cond = ta.crossover(fast_sma, mid_sma)[-1] and mid_sma[-1] > slow_sma[-1]
exit_cond = ta.crossunder(fast_sma, mid_sma)[-1]

if long_cond:
    strategy.entry("Long", strategy.LONG)
if exit_cond:
    strategy.close("Long")

p1 = plot(fast_sma, title="Fast SMA", color="lime")
p2 = plot(mid_sma, title="Mid SMA", color="orange")
p3 = plot(slow_sma, title="Slow SMA", color="red")
fill(p1, p2, color="rgba(0,255,0,0.08)")

# --- Rich annotations ---
n = len(close)
cross_up = ta.crossover(fast_sma, mid_sma)
cross_down = ta.crossunder(fast_sma, mid_sma)
atr = ta.atr(high, low, close, 14)
last_signal_idx = -100

for i in range(slow_len, n):
    if cross_up[i] and mid_sma[i] > slow_sma[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Golden Cross\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(slow_sma[i])
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

    elif cross_down[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Death Cross",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
