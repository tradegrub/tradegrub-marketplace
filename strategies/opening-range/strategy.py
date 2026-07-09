# Opening Range Breakout Strategy
from tg_scripting import *
import numpy as np

strategy("Opening Range", overlay=True)

or_bars = input.int(5, "Opening Range Bars", minval=1, maxval=30)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_tp_mult = input.float(2.0, "ATR Take Profit Multiplier", minval=1.0, maxval=5.0)
atr_sl_mult = input.float(1.0, "ATR Stop Loss Multiplier", minval=0.5, maxval=3.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculate opening range as highest/lowest of first N bars
or_high = ta.highest(high, or_bars)
or_low = ta.lowest(low, or_bars)
or_mid = (or_high + or_low) / 2
atr = ta.atr(high, low, close, atr_length)

# Breakout above/below the opening range
long_signal = ta.crossover(close, or_high)
short_signal = ta.crossunder(close, or_low)

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Take profit and stop loss based on ATR
strategy.exit("Long TP/SL", from_entry="Long",
              limit=close[-1] + atr[-1] * atr_tp_mult,
              stop=close[-1] - atr[-1] * atr_sl_mult)
strategy.exit("Short TP/SL", from_entry="Short",
              limit=close[-1] - atr[-1] * atr_tp_mult,
              stop=close[-1] + atr[-1] * atr_sl_mult)

# Exit at midline as fallback
if ta.crossunder(close, or_mid)[-1]:
    strategy.close("Long")

if ta.crossover(close, or_mid)[-1]:
    strategy.close("Short")

p1 = plot(or_high, title="OR High", color="green")
p2 = plot(or_low, title="OR Low", color="red")
plot(or_mid, title="OR Mid", color="orange")
fill(p1, p2, color="rgba(255, 152, 0, 0.06)")

plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 20

for i in range(or_bars, n):
    if long_signal[i] and (i - last_signal_idx) > or_bars * 2:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_sl_mult)
            tp_price = float(close[i] + atr[i] * atr_tp_mult)
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

    elif short_signal[i] and (i - last_signal_idx) > or_bars * 2:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_sl_mult)
            tp_price = float(close[i] - atr[i] * atr_tp_mult)
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
