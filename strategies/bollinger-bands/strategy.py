# Bollinger Bands Strategy
from tg_scripting import *

length = input.int("Length", 20, minval=5, maxval=200)
mult = input.float("Std Dev Multiplier", 2.0, minval=0.5, maxval=5.0)

upper, basis, lower = ta.bbands(close, length, mult)

if ta.crossover(close, lower):
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(close, upper):
    strategy.close("Long")

plot(upper, "Upper Band", color="red")
plot(basis, "Basis", color="gray")
plot(lower, "Lower Band", color="green")
