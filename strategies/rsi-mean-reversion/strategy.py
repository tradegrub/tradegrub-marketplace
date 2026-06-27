# RSI Mean Reversion Strategy
from tg_scripting import *

length = input.int(14, "RSI Length", minval=2, maxval=100)
oversold = input.int(30, "Oversold Level", minval=5, maxval=50)
overbought = input.int(70, "Overbought Level", minval=50, maxval=95)

rsi = ta.rsi(close, length)

if ta.crossover(rsi, oversold):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(rsi, overbought):
    strategy.close("Long")

plot(rsi, "RSI", color="purple")
