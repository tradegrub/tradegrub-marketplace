# Moving Average Crossover Strategy
from tg_scripting import *

fast_period = input.int("Fast Period", 9, minval=2, maxval=200)
slow_period = input.int("Slow Period", 21, minval=2, maxval=500)

fast_ma = ta.sma(close, fast_period)
slow_ma = ta.sma(close, slow_period)

if ta.crossover(fast_ma, slow_ma):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(fast_ma, slow_ma):
    strategy.close("Long")

plot(fast_ma, "Fast MA", color="blue")
plot(slow_ma, "Slow MA", color="orange")
