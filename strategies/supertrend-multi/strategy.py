# Multi-Timeframe Supertrend Strategy
from tg_scripting import *

length1 = input.int(10, "Fast Supertrend Length", minval=3, maxval=50)
mult1 = input.float(2.0, "Fast Multiplier", minval=0.5, maxval=5.0)
length2 = input.int(20, "Slow Supertrend Length", minval=5, maxval=100)
mult2 = input.float(3.0, "Slow Multiplier", minval=1.0, maxval=8.0)

st_fast = ta.supertrend(high, low, close, length1, mult1)
st_slow = ta.supertrend(high, low, close, length2, mult2)

fast_bull = close[-1] > st_fast[-1]
fast_bear = close[-1] < st_fast[-1]
slow_bull = close[-1] > st_slow[-1]
slow_bear = close[-1] < st_slow[-1]

# Enter long when both supertrends are bullish
if fast_bull and slow_bull:
    strategy.entry("Long", strategy.LONG)

# Enter short when both supertrends are bearish
if fast_bear and slow_bear:
    strategy.entry("Short", strategy.SHORT)

# Exit when fast supertrend flips
if fast_bear:
    strategy.close("Long")
if fast_bull:
    strategy.close("Short")

plot(st_fast, title="Fast Supertrend", color="green")
plot(st_slow, title="Slow Supertrend", color="red")
plot(close, title="Close", color="gray")
