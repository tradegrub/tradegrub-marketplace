# RSI Mean Reversion Strategy
from tg_scripting import *

length = input.int("RSI Length", 14, minval=2, maxval=100)
oversold = input.int("Oversold Level", 30, minval=5, maxval=50)
overbought = input.int("Overbought Level", 70, minval=50, maxval=95)

rsi = ta.rsi(close, length)

if ta.crossover(rsi, oversold):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(rsi, overbought):
    strategy.close("Long")

plot(rsi, "RSI", color="purple")
