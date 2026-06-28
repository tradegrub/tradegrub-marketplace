# N-Bar Range Breakout Strategy
from tg_scripting import *

length = input.int(20, "Range Lookback", minval=5, maxval=100)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_sl_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=4.0)
use_close_filter = input.bool(True, "Require Close Outside Range")

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

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at midline or ATR stop
if ta.crossunder(close, range_mid)[-1]:
    strategy.close("Long")

if ta.crossover(close, range_mid)[-1]:
    strategy.close("Short")

strategy.exit("Long SL", from_entry="Long", trail_offset=atr[-1] * atr_sl_mult)
strategy.exit("Short SL", from_entry="Short", trail_offset=atr[-1] * atr_sl_mult)

p1 = plot(range_high, title="Range High", color="green")
p2 = plot(range_low, title="Range Low", color="red")
plot(range_mid, title="Range Mid", color="gray")
fill(p1, p2, color="rgba(0, 150, 136, 0.06)")

plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")
