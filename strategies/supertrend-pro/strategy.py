from tg_scripting import *

atr_period = input.int(10, "ATR Period", minval=1, maxval=100)
multiplier = input.float(3.0, "Multiplier", minval=0.5, maxval=10.0)
use_trailing = input.bool(True, "Trailing Stop")

atr_val = ta.atr(atr_period)
supertrend, direction = ta.supertrend(atr_period, multiplier)

if ta.crossover(direction, 0):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(direction, 0):
    strategy.entry("Short", strategy.SHORT)

if use_trailing:
    trail_offset = atr_val[-1] * multiplier
    if direction[-1] > 0:
        strategy.exit("Trail Long", "Long", trail_offset=trail_offset)
    else:
        strategy.exit("Trail Short", "Short", trail_offset=trail_offset)

bull = direction[-1] > 0
plot(supertrend, "SuperTrend", color="green" if bull else "red", linewidth=2)
plotshape(ta.crossover(direction, 0), "Buy", shape="triangleup", location="belowbar", color="green", size="small")
plotshape(ta.crossunder(direction, 0), "Sell", shape="triangledown", location="abovebar", color="red", size="small")
