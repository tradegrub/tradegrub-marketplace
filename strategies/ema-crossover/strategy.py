# EMA Crossover Strategy
from tg_scripting import *
import numpy as np

indicator("EMA Crossover", overlay=True)

fast_len = input.int(9, "Fast EMA Length", minval=2, maxval=50)
slow_len = input.int(21, "Slow EMA Length", minval=5, maxval=200)
trend_len = input.int(100, "Trend Filter EMA", minval=20, maxval=500)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

fast_ema = ta.ema(close, fast_len)
slow_ema = ta.ema(close, slow_len)
trend_ema = ta.ema(close, trend_len)

long_cond = ta.crossover(fast_ema, slow_ema)[-1] and close[-1] > trend_ema[-1]
exit_cond = ta.crossunder(fast_ema, slow_ema)[-1]

if long_cond:
    strategy.entry("Long", strategy.LONG)
if exit_cond:
    strategy.close("Long")

p1 = plot(fast_ema, title="Fast EMA", color="orange")
p2 = plot(slow_ema, title="Slow EMA", color="blue")
plot(trend_ema, title="Trend Filter", color="gray")
fill(p1, p2, color="rgba(0,150,255,0.1)")

# --- Rich annotations ---
n = len(close)
cross_up = ta.crossover(fast_ema, slow_ema)
cross_down = ta.crossunder(fast_ema, slow_ema)
atr_ann = ta.atr(high, low, close, 14)
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if cross_up[i] and close[i] > trend_ema[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Golden Cross",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr_ann[i] * 1.5)
            tp_price = float(close[i] + atr_ann[i] * 3.0)
            end_bar = min(i + 30, n - 1)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Death Cross",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
