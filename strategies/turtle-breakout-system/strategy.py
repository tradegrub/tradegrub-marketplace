# Turtle Breakout System — the complete two-system rules, not just the channel.
from tg_scripting import *
import numpy as np

indicator("Turtle Breakout System", overlay=True)

entry_fast = input.int(20, "System 1 entry (bars)", minval=5, maxval=100)
exit_fast = input.int(10, "System 1 exit (bars)", minval=3, maxval=50)
entry_slow = input.int(55, "System 2 entry (bars)", minval=20, maxval=200)
exit_slow = input.int(20, "System 2 exit (bars)", minval=5, maxval=100)
n_length = input.int(20, "N (ATR) length", minval=5, maxval=100)
stop_n = input.float(2.0, "Stop distance in N", minval=0.5, maxval=5.0)
max_units = input.int(4, "Max pyramid units", minval=1, maxval=6)

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
n_bars = len(c)

N = ta.atr(high, low, close, n_length)

def rolling_extreme(arr, length, use_max):
    out = np.full(len(arr), np.nan)
    for i in range(length, len(arr)):
        window = arr[i - length:i]
        out[i] = window.max() if use_max else window.min()
    return out

# Entry channels exclude the current bar, so a breakout is measured against
# history rather than against itself.
fast_hi = rolling_extreme(h, entry_fast, True)
fast_lo = rolling_extreme(l, entry_fast, False)
slow_hi = rolling_extreme(h, entry_slow, True)
slow_lo = rolling_extreme(l, entry_slow, False)
exit_hi_f = rolling_extreme(h, exit_fast, True)
exit_lo_f = rolling_extreme(l, exit_fast, False)
exit_hi_s = rolling_extreme(h, exit_slow, True)
exit_lo_s = rolling_extreme(l, exit_slow, False)

units = 0
direction = 0
last_entry = 0.0
stop = 0.0
long_entry = np.zeros(n_bars, dtype=bool)
short_entry = np.zeros(n_bars, dtype=bool)
add_on = np.zeros(n_bars, dtype=bool)

for i in range(entry_slow + 1, n_bars):
    strategy.set_bar_index(i)
    unit_n = float(N[i]) if N[i] == N[i] else 0.0
    if unit_n <= 0:
        continue

    if direction == 0:
        # System 2 (55 bar) always takes its signal; System 1 (20 bar) is the
        # faster entry. Either one opens the first unit.
        if c[i] > slow_hi[i] or c[i] > fast_hi[i]:
            strategy.entry("Long", strategy.LONG)
            direction, units, last_entry = 1, 1, float(c[i])
            stop = last_entry - stop_n * unit_n
            long_entry[i] = True
        elif c[i] < slow_lo[i] or c[i] < fast_lo[i]:
            strategy.entry("Short", strategy.SHORT)
            direction, units, last_entry = -1, 1, float(c[i])
            stop = last_entry + stop_n * unit_n
            short_entry[i] = True
        continue

    if direction == 1:
        # Pyramid every half-N of favourable movement, up to the unit cap.
        if units < max_units and c[i] >= last_entry + 0.5 * unit_n:
            strategy.entry("Long", strategy.LONG)
            units += 1
            last_entry = float(c[i])
            stop = last_entry - stop_n * unit_n
            add_on[i] = True
        if c[i] <= stop or c[i] < exit_lo_f[i] or c[i] < exit_lo_s[i]:
            strategy.close("Long")
            direction, units = 0, 0
    else:
        if units < max_units and c[i] <= last_entry - 0.5 * unit_n:
            strategy.entry("Short", strategy.SHORT)
            units += 1
            last_entry = float(c[i])
            stop = last_entry + stop_n * unit_n
            add_on[i] = True
        if c[i] >= stop or c[i] > exit_hi_f[i] or c[i] > exit_hi_s[i]:
            strategy.close("Short")
            direction, units = 0, 0

p1 = plot(slow_hi, title="55-bar high", color="green")
p2 = plot(slow_lo, title="55-bar low", color="red")
plot(fast_hi, title="20-bar high", color="rgba(0,230,118,0.4)")
plot(fast_lo, title="20-bar low", color="rgba(239,83,80,0.4)")
fill(p1, p2, color="rgba(66, 165, 245, 0.05)")

plotshape(long_entry, title="Turtle long", style="triangleup", location="belowbar", color="green")
plotshape(short_entry, title="Turtle short", style="triangledown", location="abovebar", color="red")
plotshape(add_on, title="Pyramid unit", style="circle", location="absolute", color="blue")
