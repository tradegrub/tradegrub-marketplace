# Standard Deviation Channel Reversion
from tg_scripting import *

length = input.int(50, "Channel Length", minval=10, maxval=200)
mult = input.float(2.0, "Std Dev Multiplier", minval=0.5, maxval=4.0)

# Linear regression as the channel center
basis = ta.linreg(close, length)
stdev = ta.stdev(close, length)

upper = basis + stdev * mult
lower = basis - stdev * mult

# Mean reversion from channel extremes
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)

if ta.crossunder(close, upper)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at regression line
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")
if ta.crossover(close, basis)[-1]:
    strategy.close("Short")

plot(upper, title="Upper Channel", color="red")
plot(basis, title="Regression Line", color="blue")
plot(lower, title="Lower Channel", color="green")
fill("Upper Channel", "Lower Channel", color="rgba(63, 81, 181, 0.08)")
