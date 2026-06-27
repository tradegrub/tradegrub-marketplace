# Moving Average Crossover Strategy
from tg_scripting import *

fast_period = input.int(9, "Fast Period", minval=2, maxval=200)
slow_period = input.int(21, "Slow Period", minval=2, maxval=500)

fast_ma = ta.sma(close, fast_period)
slow_ma = ta.sma(close, slow_period)

if ta.crossover(fast_ma, slow_ma):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(fast_ma, slow_ma):
    strategy.close("Long")

plot(fast_ma, title="Fast MA", color="blue")
plot(slow_ma, title="Slow MA", color="orange")
