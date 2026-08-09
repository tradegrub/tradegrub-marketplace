# Swing Extreme Reversal — the extreme plus the rejection, not just the extreme.
from tg_scripting import *
import numpy as np

indicator("Swing Extreme Reversal", overlay=True)

lookback = input.int(20, "Extreme lookback", minval=3, maxval=200)
atr_length = input.int(14, "ATR length", minval=2, maxval=100)
reject_mult = input.float(0.5, "Rejection in ATR", minval=0.1, maxval=3.0)
confirm_bars = input.int(2, "Confirmation bars", minval=1, maxval=10)

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
n = len(c)
atr = ta.atr(high, low, close, atr_length)

top = np.zeros(n, dtype=bool)
bottom = np.zeros(n, dtype=bool)

for i in range(lookback + confirm_bars, n):
    pivot = i - confirm_bars
    a = float(atr[pivot]) if atr[pivot] == atr[pivot] else 0.0
    if a <= 0:
        continue

    window_h = h[pivot - lookback:pivot]
    window_l = l[pivot - lookback:pivot]
    if not (np.isfinite(window_h).any() and np.isfinite(window_l).any()):
        continue

    # The extreme has to be a genuine multi-bar extreme, and the bars after it
    # have to have travelled a real distance back — an ATR-scaled distance, so
    # the same setting works on a quiet index and a volatile small cap.
    made_high = h[pivot] > float(np.nanmax(window_h))
    made_low = l[pivot] < float(np.nanmin(window_l))

    rejected_down = c[i] <= h[pivot] - reject_mult * a
    rejected_up = c[i] >= l[pivot] + reject_mult * a

    if made_high and rejected_down:
        top[i] = True
    elif made_low and rejected_up:
        bottom[i] = True

plotshape(bottom, title="Reversal up", style="triangleup", location="belowbar", color="green")
plotshape(top, title="Reversal down", style="triangledown", location="abovebar", color="red")

for i in range(n):
    if top[i]:
        label.new(x=i, y=float(h[i]), text="REV", style=label.style_label_down,
                  color="rgba(239,83,80,0.2)", textcolor="#ef5350", size="small")
    elif bottom[i]:
        label.new(x=i, y=float(l[i]), text="REV", style=label.style_label_up,
                  color="rgba(0,230,118,0.2)", textcolor="#00e676", size="small")
