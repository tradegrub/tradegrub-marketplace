# Heikin-Ashi Trend Following Strategy
from tg_scripting import *

ema_fast = input.int(8, "Fast EMA Length", minval=3, maxval=20)
ema_slow = input.int(21, "Slow EMA Length", minval=10, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_trail = input.float(2.0, "ATR Trailing Multiplier", minval=1.0, maxval=5.0)

# Compute Heikin-Ashi candles using numpy
ha_close = (open + high + low + close) / 4.0

# For ha_open, use rolling calculation: start with (open+close)/2, then average with prior ha_open
ha_open = np.empty_like(close)
ha_open[0] = (open[0] + close[0]) / 2.0
for i in range(1, len(close)):
    ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0

ha_high = np.maximum(high, np.maximum(ha_open, ha_close))
ha_low = np.minimum(low, np.minimum(ha_open, ha_close))

# HA trend signals
ha_bullish = ha_close[-1] > ha_open[-1]
ha_bearish = ha_close[-1] < ha_open[-1]

# No lower wick on bullish = strong trend up
ha_strong_bull = ha_bullish and (ha_low[-1] == np.minimum(ha_open[-1], ha_close[-1]))
# No upper wick on bearish = strong trend down
ha_strong_bear = ha_bearish and (ha_high[-1] == np.maximum(ha_open[-1], ha_close[-1]))

# EMA trend confirmation on HA close
fast_ema = ta.ema(ha_close, ema_fast)
slow_ema = ta.ema(ha_close, ema_slow)
atr = ta.atr(high, low, close, atr_len)

bull_trend = fast_ema[-1] > slow_ema[-1]
bear_trend = fast_ema[-1] < slow_ema[-1]

# Entry on HA color flip with EMA confirmation
ha_flip_bull = ha_bullish and (ha_close[-2] < ha_open[-2]) and bull_trend
ha_flip_bear = ha_bearish and (ha_close[-2] > ha_open[-2]) and bear_trend

if ha_flip_bull:
    strategy.entry("Long", strategy.LONG)

if ha_flip_bear:
    strategy.entry("Short", strategy.SHORT)

# Trailing stop exits
if ha_bearish and bull_trend == False:
    strategy.close("Long")
if ha_bullish and bear_trend == False:
    strategy.close("Short")

plotcandle(ha_open, ha_high, ha_low, ha_close, title="Heikin-Ashi")
plot(fast_ema, title="Fast EMA", color="blue")
plot(slow_ema, title="Slow EMA", color="red")
plotshape(ha_flip_bull, title="HA Bull Flip", style="triangleup", location="belowbar", color="green")
plotshape(ha_flip_bear, title="HA Bear Flip", style="triangledown", location="abovebar", color="red")
