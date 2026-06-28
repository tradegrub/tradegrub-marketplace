# Volatility Breakout (Bollinger Band Width Expansion)
from tg_scripting import *

bb_length = input.int(20, "BB Length", minval=10, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=1.0, maxval=4.0)
squeeze_pctile = input.float(20.0, "Squeeze Percentile", minval=5.0, maxval=50.0)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_sl_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=4.0)

# Bollinger Bands and width
upper, basis, lower = ta.bb(close, bb_length, bb_mult)
bbw = ta.bbw(close, bb_length, bb_mult)
atr = ta.atr(high, low, close, atr_length)

# Detect squeeze: BBW below its own percentile threshold
bbw_min = ta.lowest(bbw, 100)
bbw_max = ta.highest(bbw, 100)
bbw_range = bbw_max - bbw_min
bbw_threshold = bbw_min + bbw_range * (squeeze_pctile / 100.0)
in_squeeze = bbw < bbw_threshold

# Breakout from squeeze
long_signal = ta.crossover(close, upper) & in_squeeze
short_signal = ta.crossunder(close, lower) & in_squeeze

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when price returns inside bands
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")

if ta.crossover(close, basis)[-1]:
    strategy.close("Short")

strategy.exit("Long SL", from_entry="Long", trail_offset=atr[-1] * atr_sl_mult)
strategy.exit("Short SL", from_entry="Short", trail_offset=atr[-1] * atr_sl_mult)

p1 = plot(upper, title="BB Upper", color="blue")
p2 = plot(lower, title="BB Lower", color="blue")
plot(basis, title="BB Basis", color="gray")
fill(p1, p2, color="rgba(33, 150, 243, 0.06)")

bgcolor(in_squeeze, color="rgba(255, 235, 59, 0.1)")
plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")
