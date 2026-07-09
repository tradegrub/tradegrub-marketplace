# Moving Average Crossover Strategy
from tg_scripting import *
import numpy as np

strategy("MA Crossover", overlay=True)

fast_period = input.int(9, "Fast Period", minval=2, maxval=200)
slow_period = input.int(21, "Slow Period", minval=2, maxval=500)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

fast_ma = ta.sma(close, fast_period)
slow_ma = ta.sma(close, slow_period)

buy = ta.crossover(fast_ma, slow_ma)
sell = ta.crossunder(fast_ma, slow_ma)
for i in range(len(close)):
    if buy[i]:
        strategy.entry("Long", strategy.LONG)
    if sell[i]:
        strategy.close("Long")

plot(fast_ma, title="Fast MA", color="blue")
plot(slow_ma, title="Slow MA", color="orange")

# --- Rich annotations ---
n = len(close)
atr = ta.atr(high, low, close, 14)
last_signal_idx = -100
cooldown = max(slow_period, 15)

for i in range(slow_period, n):
    if buy[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="Golden Cross",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2.0)
            tp_price = float(close[i] + atr[i] * 4.0)
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

    elif sell[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="Death Cross",
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
