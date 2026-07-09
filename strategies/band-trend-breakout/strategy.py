# Band Trend Breakout
from tg_scripting import *
import numpy as np

indicator("Band Trend Breakout", overlay=True)

ema_len = input.int(20, "EMA Length", minval=5, maxval=100)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
multiplier = input.float(2.0, "Band Multiplier", minval=0.5, maxval=5.0)
show_labels = input.bool(True, "Show Labels")

# Calculate adaptive bands
center = ta.ema(close, ema_len)
width = ta.atr(high, low, close, atr_len) * multiplier
upper_band = center + width
lower_band = center - width

# Entry signals: breakout above/below bands
long_entry = ta.crossover(close, upper_band)
short_entry = ta.crossunder(close, lower_band)

# Exit signals: trail back to center line
long_exit = ta.crossunder(close, center)
short_exit = ta.crossover(close, center)

# Strategy entries
n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if long_entry[i]:
        strategy.entry("Long", strategy.LONG)

    if short_entry[i]:
        strategy.entry("Short", strategy.SHORT)

    # Strategy exits (trailing to center)
    if long_exit[i]:
        strategy.close("Long")

    if short_exit[i]:
        strategy.close("Short")

# Plot bands
p_upper = plot(upper_band, title="Upper Band", color="green")
p_lower = plot(lower_band, title="Lower Band", color="red")
plot(center, title="Center EMA", color="#42a5f5")
fill(p_upper, p_lower, color="rgba(33, 150, 243, 0.06)")

# Shape markers
plotshape(long_entry, title="Long Entry", style="triangleup", location="belowbar", color="green")
plotshape(short_entry, title="Short Entry", style="triangledown", location="abovebar", color="red")
plotshape(long_exit, title="Long Exit", style="cross", location="abovebar", color="orange")
plotshape(short_exit, title="Short Exit", style="cross", location="belowbar", color="orange")

# Labels
if show_labels:
    n = len(close)
    cooldown = 15
    last_idx = -100

    for i in range(1, n):
        if long_entry[i] and (i - last_idx) > cooldown:
            last_idx = i
            label.new(x=i, y=float(low[i]), text="LONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="tiny")
        elif short_entry[i] and (i - last_idx) > cooldown:
            last_idx = i
            label.new(x=i, y=float(high[i]), text="SHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="tiny")
        elif long_exit[i] and (i - last_idx) > cooldown:
            last_idx = i
            label.new(x=i, y=float(high[i]), text="EXIT L",
                      style=label.style_label_down, color="#ff9800",
                      textcolor="#000000", size="tiny")
        elif short_exit[i] and (i - last_idx) > cooldown:
            last_idx = i
            label.new(x=i, y=float(low[i]), text="EXIT S",
                      style=label.style_label_up, color="#ff9800",
                      textcolor="#000000", size="tiny")
