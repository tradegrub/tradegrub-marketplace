# Donchian Channel Breakout (Turtle Trading)
from tg_scripting import *

entry_length = input.int(20, "Entry Channel Length", minval=5, maxval=100)
exit_length = input.int(10, "Exit Channel Length", minval=3, maxval=50)
use_atr_stop = input.bool(True, "Use ATR Trailing Stop")
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Stop Multiplier", minval=0.5, maxval=5.0)

# Donchian channels for entry and exit
entry_upper, entry_lower, entry_basis = ta.donchian(high, low, entry_length)
exit_upper, exit_lower, exit_basis = ta.donchian(high, low, exit_length)
atr = ta.atr(high, low, close, atr_length)

# Classic Turtle entry: breakout above/below channel
long_entry = ta.crossover(close, entry_upper)
short_entry = ta.crossunder(close, entry_lower)

if long_entry[-1]:
    strategy.entry("Long", strategy.LONG)

if short_entry[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit on opposite exit channel break
if ta.crossunder(close, exit_lower)[-1]:
    strategy.close("Long")

if ta.crossover(close, exit_upper)[-1]:
    strategy.close("Short")

# Optional ATR trailing stop
if use_atr_stop:
    strategy.exit("Long SL", from_entry="Long", trail_offset=atr[-1] * atr_mult)
    strategy.exit("Short SL", from_entry="Short", trail_offset=atr[-1] * atr_mult)

p1 = plot(entry_upper, title="Entry Upper", color="green")
p2 = plot(entry_lower, title="Entry Lower", color="red")
plot(entry_basis, title="Entry Basis", color="gray")
plot(exit_upper, title="Exit Upper", color="rgba(0,200,0,0.4)")
plot(exit_lower, title="Exit Lower", color="rgba(200,0,0,0.4)")
fill(p1, p2, color="rgba(0, 150, 136, 0.06)")

plotshape(long_entry, title="Long Signal", style="triangleup", location="belowbar", color="green")
plotshape(short_entry, title="Short Signal", style="triangledown", location="abovebar", color="red")
