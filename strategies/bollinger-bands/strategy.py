# Bollinger Bands Strategy
from tg_scripting import *

length = input.int(20, "Length", minval=5, maxval=200)
mult = input.float(2.0, "Std Dev Multiplier", minval=0.5, maxval=5.0)

upper, basis, lower = ta.bbands(close, length, mult)

if ta.crossover(close, lower):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(close, upper):
    strategy.close("Long")

plot(upper, "Upper Band", color="red")
plot(basis, "Basis", color="gray")
plot(lower, "Lower Band", color="green")
