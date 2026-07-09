# MACD Crossover Strategy
from tg_scripting import *
import numpy as np

strategy("MACD Crossover", overlay=True)

fast_length = input.int(12, "Fast Length", minval=2, maxval=100)
slow_length = input.int(26, "Slow Length", minval=2, maxval=200)
signal_length = input.int(9, "Signal Length", minval=2, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

macd_line, signal_line, histogram = ta.macd(close, fast_length, slow_length, signal_length)
atr = ta.atr(high, low, close, 14)

buy = ta.crossover(macd_line, signal_line)
sell = ta.crossunder(macd_line, signal_line)

n = len(close)
last_signal_idx = -100
cooldown = 15

for i in range(len(close)):
    if buy[i]:
        strategy.entry("Long", strategy.LONG)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(low[i]),
                    text="LONG\nMACD Cross",
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

    if sell[i]:
        strategy.close("Long")

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(high[i]),
                    text="EXIT\nMACD Cross",
                    style=label.style_label_down,
                    color="#ef5350",
                    textcolor="#ffffff",
                    size="normal"
                )

plot(macd_line, title="MACD", color="blue")
plot(signal_line, title="Signal", color="orange")
