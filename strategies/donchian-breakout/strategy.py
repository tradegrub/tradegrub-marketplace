# Donchian Channel Breakout (Turtle Trading)
from tg_scripting import *
import numpy as np

indicator("Donchian Breakout", overlay=True)

entry_length = input.int(20, "Entry Channel Length", minval=5, maxval=100)
exit_length = input.int(10, "Exit Channel Length", minval=3, maxval=50)
use_atr_stop = input.bool(True, "Use ATR Trailing Stop")
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Donchian channels for entry and exit
entry_upper, entry_lower, entry_basis = ta.donchian(high, low, entry_length)
exit_upper, exit_lower, exit_basis = ta.donchian(high, low, exit_length)
atr = ta.atr(high, low, close, atr_length)

# Classic Turtle entry: breakout above/below channel
long_entry = ta.crossover(close, entry_upper)
short_entry = ta.crossunder(close, entry_lower)

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if long_entry[i]:
        strategy.entry("Long", strategy.LONG)

    if short_entry[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit on opposite exit channel break
    if ta.crossunder(close, exit_lower)[i]:
        strategy.close("Long")

    if ta.crossover(close, exit_upper)[i]:
        strategy.close("Short")

    # Optional ATR trailing stop
    if use_atr_stop:
        strategy.exit("Long SL", from_entry="Long", trail_offset=atr[i] * atr_mult)
        strategy.exit("Short SL", from_entry="Short", trail_offset=atr[i] * atr_mult)

p1 = plot(entry_upper, title="Entry Upper", color="green")
p2 = plot(entry_lower, title="Entry Lower", color="red")
plot(entry_basis, title="Entry Basis", color="gray")
plot(exit_upper, title="Exit Upper", color="rgba(0,200,0,0.4)")
plot(exit_lower, title="Exit Lower", color="rgba(200,0,0,0.4)")
fill(p1, p2, color="rgba(0, 150, 136, 0.06)")

plotshape(long_entry, title="Long Signal", style="triangleup", location="belowbar", color="green")
plotshape(short_entry, title="Short Signal", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30
channel_label_placed = False

for i in range(1, n):
    if long_entry[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG\nBreakout",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(exit_lower[i])
            tp_price = float(close[i] + (close[i] - exit_lower[i]) * 2)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop (Exit Low)",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit (2:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_entry[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT\nBreakdown",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(exit_upper[i])
            tp_price = float(close[i] - (exit_upper[i] - close[i]) * 2)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop (Exit High)",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit (2:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

    # Label the Donchian channel once
    if show_labels and not channel_label_placed and i > entry_length:
        channel_label_placed = True
        label.new(x=i, y=float(entry_upper[i]), text="Donchian Channel",
                  style=label.style_label_down, color="rgba(136,136,136,0.3)",
                  textcolor="#888888", size="normal")
