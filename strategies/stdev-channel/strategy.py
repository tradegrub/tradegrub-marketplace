# Standard Deviation Channel Reversion
from tg_scripting import *
import numpy as np

strategy("Stdev Channel", overlay=True)

length = input.int(50, "Channel Length", minval=10, maxval=200)
mult = input.float(2.0, "Std Dev Multiplier", minval=0.5, maxval=4.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Linear regression as the channel center
basis = ta.linreg(close, length)
stdev = ta.stdev(close, length)

upper = basis + stdev * mult
lower = basis - stdev * mult

# Mean reversion from channel extremes
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)

if ta.crossunder(close, upper)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at regression line
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")
if ta.crossover(close, basis)[-1]:
    strategy.close("Short")

plot(upper, title="Upper Channel", color="red")
plot(basis, title="Regression Line", color="blue")
plot(lower, title="Lower Channel", color="green")
fill("Upper Channel", "Lower Channel", color="rgba(63, 81, 181, 0.08)")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 25
cooldown = length // 2

long_cross = ta.crossover(close, lower)
short_cross = ta.crossunder(close, upper)

for i in range(length, n):
    if long_cross[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Lower Band\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(lower[i] - stdev[i] * 0.5)
            tp_price = float(basis[i])
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
            label.new(x=i + 2, y=tp_price, text="Regression",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_cross[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Upper Band\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(upper[i] + stdev[i] * 0.5)
            tp_price = float(basis[i])
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
            label.new(x=i + 2, y=tp_price, text="Regression",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")
