# Failed Breakout Fade — trade the trap, not the breakout.
from tg_scripting import *
import numpy as np

indicator("Failed Breakout Fade", overlay=True)

lookback = input.int(20, "Range lookback", minval=5, maxval=100)
fail_within = input.int(3, "Bars allowed to fail", minval=1, maxval=10)
atr_length = input.int(14, "ATR length", minval=5, maxval=50)
stop_mult = input.float(1.0, "Stop in ATR beyond the extreme", minval=0.3, maxval=4.0)
target_mult = input.float(2.0, "Target in ATR", minval=0.5, maxval=6.0)

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
n = len(c)
atr = ta.atr(high, low, close, atr_length)

prior_hi = np.full(n, np.nan)
prior_lo = np.full(n, np.nan)
for i in range(lookback, n):
    prior_hi[i] = h[i - lookback:i].max()
    prior_lo[i] = l[i - lookback:i].min()

fade_short = np.zeros(n, dtype=bool)
fade_long = np.zeros(n, dtype=bool)

# A breakout is only a trap once price is back inside the range, so each
# candidate is held open for a few bars and then judged.
pending_up = -1
pending_down = -1
in_trade = 0
entry_price = 0.0
stop_price = 0.0
target_price = 0.0

for i in range(lookback + 1, n):
    strategy.set_bar_index(i)
    a = float(atr[i]) if atr[i] == atr[i] else 0.0
    if a <= 0:
        continue

    if h[i] > prior_hi[i]:
        pending_up = i
    if l[i] < prior_lo[i]:
        pending_down = i

    if in_trade == 0:
        if pending_up > 0 and 0 < i - pending_up <= fail_within and c[i] < prior_hi[pending_up]:
            strategy.entry("Short", strategy.SHORT)
            in_trade, entry_price = -1, float(c[i])
            stop_price = float(h[pending_up]) + stop_mult * a
            target_price = entry_price - target_mult * a
            fade_short[i] = True
            pending_up = -1
        elif pending_down > 0 and 0 < i - pending_down <= fail_within and c[i] > prior_lo[pending_down]:
            strategy.entry("Long", strategy.LONG)
            in_trade, entry_price = 1, float(c[i])
            stop_price = float(l[pending_down]) - stop_mult * a
            target_price = entry_price + target_mult * a
            fade_long[i] = True
            pending_down = -1
    elif in_trade == 1:
        if c[i] <= stop_price or c[i] >= target_price:
            strategy.close("Long")
            in_trade = 0
    else:
        if c[i] >= stop_price or c[i] <= target_price:
            strategy.close("Short")
            in_trade = 0

p1 = plot(prior_hi, title="Range high", color="green")
p2 = plot(prior_lo, title="Range low", color="red")
fill(p1, p2, color="rgba(171, 71, 188, 0.05)")

plotshape(fade_long, title="Fade long", style="triangleup", location="belowbar", color="green")
plotshape(fade_short, title="Fade short", style="triangledown", location="abovebar", color="red")

for i in range(lookback + 1, n):
    if fade_short[i]:
        label.new(x=i, y=float(high[i]), text="FAILED\nBREAKOUT", style=label.style_label_down,
                  color="rgba(239,83,80,0.2)", textcolor="#ef5350", size="small")
    elif fade_long[i]:
        label.new(x=i, y=float(low[i]), text="FAILED\nBREAKDOWN", style=label.style_label_up,
                  color="rgba(0,230,118,0.2)", textcolor="#00e676", size="small")
