# Holding Period Exit — time is the exit rule, not price.
from tg_scripting import *
import numpy as np

indicator("Holding Period Exit", overlay=True)

fast_len = input.int(10, "Fast MA length", minval=2, maxval=100)
slow_len = input.int(30, "Slow MA length", minval=5, maxval=300)
hold_bars = input.int(10, "Holding period (bars)", minval=1, maxval=200)
atr_length = input.int(14, "ATR length", minval=5, maxval=50)
stop_mult = input.float(2.0, "Disaster stop in ATR", minval=0.0, maxval=6.0)
allow_short = input.bool(True, "Trade the short side")

c = np.asarray(close, dtype=float)
n = len(c)
fast = ta.sma(close, fast_len)
slow = ta.sma(close, slow_len)
atr = ta.atr(high, low, close, atr_length)

long_sig = ta.crossover(fast, slow)
short_sig = ta.crossunder(fast, slow)

entry_bar = -1
side = 0
stop_price = 0.0
opened = np.zeros(n, dtype=bool)
timed_out = np.zeros(n, dtype=bool)

for i in range(slow_len + 1, n):
    strategy.set_bar_index(i)
    a = float(atr[i]) if atr[i] == atr[i] else 0.0

    if side != 0:
        # The holding period is absolute: it closes winners and losers alike,
        # which is the whole point of testing an entry in isolation.
        if i - entry_bar >= hold_bars:
            strategy.close("Long" if side == 1 else "Short")
            side, entry_bar = 0, -1
            timed_out[i] = True
        elif stop_mult > 0 and a > 0:
            if side == 1 and c[i] <= stop_price:
                strategy.close("Long")
                side, entry_bar = 0, -1
            elif side == -1 and c[i] >= stop_price:
                strategy.close("Short")
                side, entry_bar = 0, -1

    if side == 0:
        if long_sig[i]:
            strategy.entry("Long", strategy.LONG)
            side, entry_bar = 1, i
            stop_price = float(c[i]) - stop_mult * a
            opened[i] = True
        elif allow_short and short_sig[i]:
            strategy.entry("Short", strategy.SHORT)
            side, entry_bar = -1, i
            stop_price = float(c[i]) + stop_mult * a
            opened[i] = True

plot(fast, title="Fast MA", color="blue")
plot(slow, title="Slow MA", color="orange")
plotshape(opened, title="Entry", style="triangleup", location="belowbar", color="green")
plotshape(timed_out, title="Timed exit", style="xcross", location="abovebar", color="gray")
