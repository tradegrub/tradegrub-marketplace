# Bollinger Band Width Squeeze Expansion
from tg_scripting import *

bb_length = input.int(20, "BB Length", minval=5, maxval=200)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=5.0)
squeeze_pct = input.float(0.02, "Squeeze Threshold", minval=0.005, maxval=0.1)
lookback = input.int(50, "Width Lookback", minval=10, maxval=200)

upper, basis, lower = ta.bb(close, bb_length, bb_mult)
bb_width = ta.bbw(close, bb_length, bb_mult)

# Detect squeeze: width at historical low
width_min = ta.lowest(bb_width, lookback)
is_squeeze = bb_width <= width_min * 1.05

# Expansion breakout after squeeze
expanding = bb_width[-1] > bb_width[-2] * 1.1

if is_squeeze[-2] and expanding:
    if close[-1] > basis[-1]:
        strategy.entry("Long", strategy.LONG)
    else:
        strategy.entry("Short", strategy.SHORT)

# Exit when price returns to basis
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")
if ta.crossover(close, basis)[-1]:
    strategy.close("Short")

plot(bb_width, title="BB Width", color="blue")
plot(width_min * 1.05, title="Squeeze Level", color="red")

bgcolor(is_squeeze[-1], color="rgba(255, 235, 59, 0.15)")
