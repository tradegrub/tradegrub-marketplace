# MACD Crossover Strategy
from tg_scripting import *

fast_length = input.int(12, "Fast Length", minval=2, maxval=100)
slow_length = input.int(26, "Slow Length", minval=2, maxval=200)
signal_length = input.int(9, "Signal Length", minval=2, maxval=50)

macd_line, signal_line, histogram = ta.macd(close, fast_length, slow_length, signal_length)

if ta.crossover(macd_line, signal_line):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(macd_line, signal_line):
    strategy.close("Long")

plot(macd_line, "MACD", color="blue")
plot(signal_line, "Signal", color="orange")
