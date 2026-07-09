# Multi-Timeframe Supertrend Strategy
from tg_scripting import *
import numpy as np

indicator("Supertrend Multi", overlay=True)

length1 = input.int(10, "Fast Supertrend Length", minval=3, maxval=50)
mult1 = input.float(2.0, "Fast Multiplier", minval=0.5, maxval=5.0)
length2 = input.int(20, "Slow Supertrend Length", minval=5, maxval=100)
mult2 = input.float(3.0, "Slow Multiplier", minval=1.0, maxval=8.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

st_fast_line, st_fast_dir = ta.supertrend(high, low, close, length1, mult1)
st_slow_line, st_slow_dir = ta.supertrend(high, low, close, length2, mult2)

fast_bull = close > st_fast_line
fast_bear = close < st_fast_line
slow_bull = close > st_slow_line
slow_bear = close < st_slow_line

for i in range(len(close)):
    # Enter long when both supertrends are bullish
    if fast_bull[i] and slow_bull[i]:
        strategy.entry("Long", strategy.LONG)
    # Enter short when both supertrends are bearish
    if fast_bear[i] and slow_bear[i]:
        strategy.entry("Short", strategy.SHORT)
    # Exit when fast supertrend flips
    if fast_bear[i]:
        strategy.close("Long")
    if fast_bull[i]:
        strategy.close("Short")

plot(st_fast_line, title="Fast Supertrend", color="green")
plot(st_slow_line, title="Slow Supertrend", color="red")
plot(close, title="Close", color="gray")

# --- Rich annotations ---
n = len(close)
atr = ta.atr(high, low, close, length2)
last_long_idx = -100
last_short_idx = -100

for i in range(max(length1, length2), n):
    both_bull = fast_bull[i] and slow_bull[i]
    both_bear = fast_bear[i] and slow_bear[i]
    prev_both_bull = fast_bull[i-1] and slow_bull[i-1] if i > 0 else False
    prev_both_bear = fast_bear[i-1] and slow_bear[i-1] if i > 0 else False

    if both_bull and not prev_both_bull and (i - last_long_idx) > 20:
        last_long_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(st_slow_line[i])
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

    elif both_bear and not prev_both_bear and (i - last_short_idx) > 20:
        last_short_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(st_slow_line[i])
            tp_price = entry_price - (sl_price - entry_price) * 2
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
            box.new(left=i, top=min(tp_price, sl_price), right=end_bar, bottom=max(tp_price, sl_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
