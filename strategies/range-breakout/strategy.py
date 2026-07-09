# N-Bar Range Breakout Strategy
from tg_scripting import *
import numpy as np

indicator("Range Breakout", overlay=True)

length = input.int(20, "Range Lookback", minval=5, maxval=100)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_sl_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=4.0)
use_close_filter = input.bool(True, "Require Close Outside Range")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# N-bar high and low range
range_high = ta.highest(high, length)
range_low = ta.lowest(low, length)
range_mid = (range_high + range_low) / 2
atr = ta.atr(high, low, close, atr_length)

# Breakout signals
if use_close_filter:
    long_signal = ta.crossover(close, range_high)
    short_signal = ta.crossunder(close, range_low)
else:
    long_signal = ta.crossover(high, range_high)
    short_signal = ta.crossunder(low, range_low)

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if long_signal[i]:
        strategy.entry("Long", strategy.LONG)

    if short_signal[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit at midline or ATR stop
    if ta.crossunder(close, range_mid)[i]:
        strategy.close("Long")

    if ta.crossover(close, range_mid)[i]:
        strategy.close("Short")

    strategy.exit("Long SL", from_entry="Long", trail_offset=atr[i] * atr_sl_mult)
    strategy.exit("Short SL", from_entry="Short", trail_offset=atr[i] * atr_sl_mult)

p1 = plot(range_high, title="Range High", color="green")
p2 = plot(range_low, title="Range Low", color="red")
plot(range_mid, title="Range Mid", color="gray")
fill(p1, p2, color="rgba(0, 150, 136, 0.06)")

plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 20
cooldown = length

for i in range(length, n):
    if long_signal[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_sl_mult)
            tp_price = float(close[i] + atr[i] * atr_sl_mult * 2)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_signal[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="BREAKOUT\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_sl_mult)
            tp_price = float(close[i] - atr[i] * atr_sl_mult * 2)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
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
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")
