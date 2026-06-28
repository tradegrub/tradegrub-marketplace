# Moving Average Envelope Breakout Strategy
from tg_scripting import *

length = input.int(20, "MA Length", minval=5, maxval=200)
pct = input.float(2.5, "Envelope Percent", minval=0.5, maxval=10.0)

basis = ta.sma(close, length)
upper = basis * (1 + pct / 100)
lower = basis * (1 - pct / 100)

# Enter long on upper envelope breakout
if ta.crossover(close, upper)[-1]:
    strategy.entry("Long", strategy.LONG)

# Enter short on lower envelope breakdown
if ta.crossunder(close, lower)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit at basis
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")
if ta.crossover(close, basis)[-1]:
    strategy.close("Short")

p1 = plot(upper, title="Upper Envelope", color="green")
p2 = plot(lower, title="Lower Envelope", color="red")
plot(basis, title="MA Basis", color="blue")
fill(p1, p2, color="rgba(100, 181, 246, 0.08)")
