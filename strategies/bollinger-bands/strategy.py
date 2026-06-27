# Bollinger Bands Strategy
from tg_scripting import *

length = input.int(20, "Length", minval=5, maxval=200)
mult = input.float(2.0, "Std Dev Multiplier", minval=0.5, maxval=5.0)

upper, basis, lower = ta.bb(close, length, mult)

if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(close, upper)[-1]:
    strategy.close("Long")

plot(upper, title="Upper Band", color="red")
plot(basis, title="Basis", color="gray")
plot(lower, title="Lower Band", color="green")
