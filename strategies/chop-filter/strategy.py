# Choppiness Index Filter + EMA Trend
from tg_scripting import *

chop_length = input.int(14, "Choppiness Length", minval=5, maxval=50)
ema_fast = input.int(12, "Fast EMA", minval=5, maxval=50)
ema_slow = input.int(26, "Slow EMA", minval=10, maxval=100)
chop_threshold = input.float(50.0, "Chop Threshold", minval=30.0, maxval=70.0)

chop = ta.chop(high, low, close, chop_length)
fast = ta.ema(close, ema_fast)
slow = ta.ema(close, ema_slow)

is_trending = chop[-1] < chop_threshold

# Only trade when market is trending (low choppiness)
if is_trending and ta.crossover(fast, slow)[-1]:
    strategy.entry("Long", strategy.LONG)

if is_trending and ta.crossunder(fast, slow)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit if market becomes choppy
if chop[-1] > 61.8:
    strategy.close_all()

plot(chop, title="Choppiness Index", color="purple")
hline(chop_threshold, title="Trend Threshold", color="green")
hline(61.8, title="Chop Threshold", color="red")
plot(fast, title="Fast EMA", color="blue")
plot(slow, title="Slow EMA", color="orange")
