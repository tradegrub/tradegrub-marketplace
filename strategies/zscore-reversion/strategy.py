# Z-Score Mean Reversion
from tg_scripting import *

length = input.int(20, "Lookback Length", minval=5, maxval=200)
entry_z = input.float(2.0, "Entry Z-Score", minval=1.0, maxval=4.0)
exit_z = input.float(0.0, "Exit Z-Score", minval=-1.0, maxval=1.0)

sma = ta.sma(close, length)
stdev = ta.stdev(close, length)
zscore = (close - sma) / stdev

# Buy when Z-score drops below negative threshold (oversold)
if ta.crossover(zscore, -entry_z)[-1]:
    strategy.entry("Long", strategy.LONG)

# Sell when Z-score rises above positive threshold (overbought)
if ta.crossunder(zscore, entry_z)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when Z-score returns to exit level
if zscore[-1] > exit_z and zscore[-2] <= exit_z:
    strategy.close("Long")
if zscore[-1] < -exit_z and zscore[-2] >= -exit_z:
    strategy.close("Short")

plot(zscore, title="Z-Score", color="blue")
hline(entry_z, title="Upper Threshold", color="red")
hline(-entry_z, title="Lower Threshold", color="green")
hline(0, title="Zero Line", color="gray")
