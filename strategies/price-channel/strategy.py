# Price Channel Breakout Strategy
from tg_scripting import *

entry_length = input.int(20, "Entry Channel Length", minval=5, maxval=100)
exit_length = input.int(10, "Exit Channel Length", minval=3, maxval=50)

highest_high = ta.highest(high, entry_length)
lowest_low = ta.lowest(low, entry_length)
mid = (highest_high + lowest_low) / 2

exit_high = ta.highest(high, exit_length)
exit_low = ta.lowest(low, exit_length)

# Enter long on highest high breakout
if close[-1] > highest_high[-2]:
    strategy.entry("Long", strategy.LONG)

# Enter short on lowest low breakdown
if close[-1] < lowest_low[-2]:
    strategy.entry("Short", strategy.SHORT)

# Exit long at exit channel low
if close[-1] < exit_low[-2]:
    strategy.close("Long")

# Exit short at exit channel high
if close[-1] > exit_high[-2]:
    strategy.close("Short")

p1 = plot(highest_high, title="Channel High", color="green")
p2 = plot(lowest_low, title="Channel Low", color="red")
plot(mid, title="Midline", color="gray")
fill(p1, p2, color="rgba(255, 193, 7, 0.08)")
