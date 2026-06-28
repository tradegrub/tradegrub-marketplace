# ATR Range Expansion Breakout
from tg_scripting import *

atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Breakout Multiplier", minval=0.5, maxval=4.0)
ma_length = input.int(20, "MA Length", minval=5, maxval=100)
exit_mult = input.float(1.0, "ATR Exit Multiplier", minval=0.5, maxval=3.0)

atr = ta.atr(high, low, close, atr_length)
basis = ta.sma(close, ma_length)

# Breakout levels based on ATR expansion from moving average
upper_band = basis + atr * atr_mult
lower_band = basis - atr * atr_mult

# Entry on ATR expansion breakout
long_signal = ta.crossover(close, upper_band)
short_signal = ta.crossunder(close, lower_band)

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit using tighter ATR band
exit_upper = basis + atr * exit_mult
exit_lower = basis - atr * exit_mult

if ta.crossunder(close, exit_lower)[-1]:
    strategy.close("Long")

if ta.crossover(close, exit_upper)[-1]:
    strategy.close("Short")

p1 = plot(upper_band, title="Upper ATR Band", color="green")
p2 = plot(lower_band, title="Lower ATR Band", color="red")
plot(basis, title="Basis MA", color="blue")
fill(p1, p2, color="rgba(33, 150, 243, 0.06)")

plotshape(long_signal, title="Long Entry", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Entry", style="triangledown", location="abovebar", color="red")
