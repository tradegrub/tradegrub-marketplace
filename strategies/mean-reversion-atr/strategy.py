# ATR-Based Mean Reversion from SMA
from tg_scripting import *

sma_length = input.int(50, "SMA Length", minval=10, maxval=200)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.5, "ATR Multiplier", minval=1.0, maxval=5.0)

sma = ta.sma(close, sma_length)
atr = ta.atr(high, low, close, atr_length)

upper_band = sma + atr * atr_mult
lower_band = sma - atr * atr_mult

# Enter when price reverts from ATR extremes
if ta.crossover(close, lower_band)[-1]:
    strategy.entry("Long", strategy.LONG)

if ta.crossunder(close, upper_band)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at SMA
if ta.crossunder(close, sma)[-1]:
    strategy.close("Long")
if ta.crossover(close, sma)[-1]:
    strategy.close("Short")

plot(sma, title="SMA", color="blue")
plot(upper_band, title="Upper ATR Band", color="red")
plot(lower_band, title="Lower ATR Band", color="green")
fill("Upper ATR Band", "Lower ATR Band", color="rgba(33, 150, 243, 0.06)")
