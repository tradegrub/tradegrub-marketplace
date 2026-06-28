# EMA Distance Mean Reversion
from tg_scripting import *

ema_length = input.int(21, "EMA Length", minval=5, maxval=200)
distance_pct = input.float(3.0, "Distance Threshold %", minval=1.0, maxval=15.0)
exit_pct = input.float(0.5, "Exit Distance %", minval=0.0, maxval=5.0)

ema = ta.ema(close, ema_length)

# Percentage distance from EMA
dist = ((close - ema) / ema) * 100

# Enter long when price is too far below EMA
if dist[-1] < -distance_pct and dist[-2] >= -distance_pct:
    strategy.entry("Long", strategy.LONG)

# Enter short when price is too far above EMA
if dist[-1] > distance_pct and dist[-2] <= distance_pct:
    strategy.entry("Short", strategy.SHORT)

# Exit when price returns near EMA
if dist[-1] > -exit_pct and dist[-2] <= -exit_pct:
    strategy.close("Long")
if dist[-1] < exit_pct and dist[-2] >= exit_pct:
    strategy.close("Short")

plot(ema, title="EMA", color="orange")
plot(dist, title="EMA Distance %", color="blue")
hline(distance_pct, title="Upper Distance", color="red")
hline(-distance_pct, title="Lower Distance", color="green")
hline(0, title="Zero", color="gray")
