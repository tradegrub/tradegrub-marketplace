# Linear Regression Deviation Reversion
from tg_scripting import *

reg_length = input.int(50, "Regression Length", minval=10, maxval=200)
dev_threshold = input.float(2.0, "Deviation Threshold %", minval=0.5, maxval=10.0)
exit_pct = input.float(0.5, "Exit Deviation %", minval=0.0, maxval=5.0)

linreg = ta.linreg(close, reg_length)

# Calculate percentage deviation from regression
deviation_pct = ((close - linreg) / linreg) * 100

# Enter when price deviates too far from regression
if deviation_pct[-1] < -dev_threshold and deviation_pct[-2] >= -dev_threshold:
    strategy.entry("Long", strategy.LONG)

if deviation_pct[-1] > dev_threshold and deviation_pct[-2] <= dev_threshold:
    strategy.entry("Short", strategy.SHORT)

# Exit when deviation normalizes
if deviation_pct[-1] > -exit_pct and deviation_pct[-2] <= -exit_pct:
    strategy.close("Long")
if deviation_pct[-1] < exit_pct and deviation_pct[-2] >= exit_pct:
    strategy.close("Short")

plot(deviation_pct, title="Deviation %", color="purple")
hline(dev_threshold, title="Upper Threshold", color="red")
hline(-dev_threshold, title="Lower Threshold", color="green")
hline(0, title="Zero", color="gray")

bgcolor(deviation_pct[-1] < -dev_threshold, color="rgba(76, 175, 80, 0.1)")
bgcolor(deviation_pct[-1] > dev_threshold, color="rgba(244, 67, 54, 0.1)")
