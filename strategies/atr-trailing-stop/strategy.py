# ATR Trailing Stop Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(3.0, "ATR Multiplier", minval=1.0, maxval=10.0)
sma_len = input.int(50, "Trend SMA Length", minval=10, maxval=200)

atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, sma_len)

# Calculate trailing stop levels
trail_long = close - atr_mult * atr
trail_short = close + atr_mult * atr

# Use highest trailing long stop as the effective stop
trail_long_stop = ta.highest(trail_long, atr_len)

# Entry: price above trend SMA
in_uptrend = close[-1] > trend_sma[-1]
in_downtrend = close[-1] < trend_sma[-1]

# Long entry when trending up and price bounces off trailing stop zone
near_stop = close[-1] < trail_long_stop[-1] * 1.02

if in_uptrend and not near_stop:
    strategy.entry("Long", strategy.LONG)

# Exit when price breaks below trailing stop
if close[-1] < trail_long_stop[-1]:
    strategy.close("Long")

# Short entry in downtrend
if in_downtrend:
    strategy.entry("Short", strategy.SHORT)

trail_short_stop = ta.lowest(trail_short, atr_len)
if close[-1] > trail_short_stop[-1]:
    strategy.close("Short")

plot(trail_long_stop, title="Long Trail Stop", color="green")
plot(trail_short_stop, title="Short Trail Stop", color="red")
plot(trend_sma, title="Trend SMA", color="orange")
