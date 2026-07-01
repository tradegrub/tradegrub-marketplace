# Price Channel Breakout Strategy
from tg_scripting import *
import numpy as np

indicator("Price Channel", overlay=True)

entry_length = input.int(20, "Entry Channel Length", minval=5, maxval=100)
exit_length = input.int(10, "Exit Channel Length", minval=3, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

highest_high = ta.highest(high, entry_length)
lowest_low = ta.lowest(low, entry_length)
mid = (highest_high + lowest_low) / 2

exit_high = ta.highest(high, exit_length)
exit_low = ta.lowest(low, exit_length)

# Enter long on highest high breakout
if close[-1] > highest_high[-2]:
    strategy.entry("Long", strategy.LONG)

# Enter short on lowest low breakdown
if close[-1] < lowest_low[-2]:
    strategy.entry("Short", strategy.SHORT)

# Exit long at exit channel low
if close[-1] < exit_low[-2]:
    strategy.close("Long")

# Exit short at exit channel high
if close[-1] > exit_high[-2]:
    strategy.close("Short")

p1 = plot(highest_high, title="Channel High", color="green")
p2 = plot(lowest_low, title="Channel Low", color="red")
plot(mid, title="Midline", color="gray")
fill(p1, p2, color="rgba(255, 193, 7, 0.08)")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 20
cooldown = entry_length

long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
for i in range(1, n):
    if close[i] > highest_high[i - 1]:
        long_sig[i] = True
    if close[i] < lowest_low[i - 1]:
        short_sig[i] = True

for i in range(entry_length, n):
    if long_sig[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(exit_low[i])
            tp_price = float(close[i] + (close[i] - exit_low[i]))
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

    elif short_sig[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="BREAKOUT\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(exit_high[i])
            tp_price = float(close[i] - (exit_high[i] - close[i]))
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
