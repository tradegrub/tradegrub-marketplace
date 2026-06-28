# Keltner Channel Mean Reversion
from tg_scripting import *

length = input.int(20, "KC Length", minval=5, maxval=200)
mult = input.float(1.5, "ATR Multiplier", minval=0.5, maxval=5.0)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)

upper, basis, lower = ta.kc(close, high, low, close, length, mult)

# Mean reversion entries
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)

if ta.crossunder(close, upper)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at basis
if ta.crossover(close, basis)[-1]:
    strategy.close("Short")
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")

plot(upper, title="KC Upper", color="red")
plot(basis, title="KC Basis", color="orange")
plot(lower, title="KC Lower", color="green")
fill("KC Upper", "KC Lower", color="rgba(255, 152, 0, 0.08)")
