# Bollinger Band Bounce Mean Reversion
from tg_scripting import *

length = input.int(20, "BB Length", minval=5, maxval=200)
mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=5.0)
exit_at_basis = input.bool(True, "Exit at Basis")

upper, basis, lower = ta.bb(close, length, mult)

# Buy when price crosses above lower band (bounce off support)
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)

# Sell when price crosses below upper band (bounce off resistance)
if ta.crossunder(close, upper)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at basis if enabled
if exit_at_basis:
    if ta.crossover(close, basis)[-1]:
        strategy.close("Short")
    if ta.crossunder(close, basis)[-1]:
        strategy.close("Long")

plot(upper, title="Upper Band", color="red")
plot(basis, title="Basis", color="gray")
plot(lower, title="Lower Band", color="green")
fill("Upper Band", "Lower Band", color="rgba(33, 150, 243, 0.08)")
