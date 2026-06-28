# Elder Impulse System
from tg_scripting import *

ema_length = input.int(13, "EMA Length", minval=5, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=5, maxval=30)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=50)
macd_signal = input.int(9, "MACD Signal", minval=3, maxval=20)

ema = ta.ema(close, ema_length)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_signal)

ema_rising = ta.change(ema, 1)
hist_rising = ta.change(hist, 1)

# Green bar: both EMA and MACD histogram rising (bullish impulse)
green_bar = (ema_rising[-1] > 0) and (hist_rising[-1] > 0)
# Red bar: both EMA and MACD histogram falling (bearish impulse)
red_bar = (ema_rising[-1] < 0) and (hist_rising[-1] < 0)

if green_bar:
    strategy.entry("Long", strategy.LONG)

if red_bar:
    strategy.entry("Short", strategy.SHORT)

# Exit long on red impulse, exit short on green impulse
if red_bar:
    strategy.close("Long")
if green_bar:
    strategy.close("Short")

plot(ema, title="EMA", color="blue")
plot(hist, title="MACD Histogram", color="gray")
bgcolor(green_bar, color="rgba(0, 200, 0, 0.15)")
bgcolor(red_bar, color="rgba(200, 0, 0, 0.15)")
