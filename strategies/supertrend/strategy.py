# Supertrend Strategy
from tg_scripting import *

atr_length = input.int(10, "ATR Length", minval=1, maxval=100)
factor = input.float(3.0, "Factor", minval=0.5, maxval=10.0)

supertrend, direction = ta.supertrend(high, low, close, atr_length, factor)

if ta.crossover(direction, 0)[-1]:
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(direction, 0)[-1]:
    strategy.close("Long")

plot(supertrend, "Supertrend", color="green")
