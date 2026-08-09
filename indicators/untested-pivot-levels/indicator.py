# Untested Pivot Levels — the levels price has not been back to.
from tg_scripting import *
import numpy as np

indicator("Untested Pivot Levels", overlay=True)

period = input.int(1, "Pivot period (bars per group)", minval=1, maxval=100)
max_levels = input.int(12, "Maximum levels kept", minval=1, maxval=60)
extend_bars = input.int(60, "Line length (bars)", minval=5, maxval=500)
show_labels = input.bool(True, "Label each level")

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
n = len(c)

# Group bars, then take each group's pivot high and low as candidate levels.
# A level counts as tested the first time a later bar's range contains it, and
# an untested level is one price has simply never come back to.
resistance: list[tuple[int, float]] = []
support: list[tuple[int, float]] = []

for start in range(0, n - period, period):
    end = min(start + period, n)
    seg_h = h[start:end]
    seg_l = l[start:end]
    if not (np.isfinite(seg_h).any() and np.isfinite(seg_l).any()):
        continue
    hi = float(np.nanmax(seg_h))
    lo = float(np.nanmin(seg_l))

    tested_hi = bool(np.any(h[end:] >= hi)) if end < n else False
    tested_lo = bool(np.any(l[end:] <= lo)) if end < n else False

    if not tested_hi:
        resistance.append((end - 1, hi))
    if not tested_lo:
        support.append((end - 1, lo))

resistance = resistance[-max_levels:]
support = support[-max_levels:]

untested_above = np.full(n, np.nan)
untested_below = np.full(n, np.nan)
if resistance:
    untested_above[-1] = min(price for _, price in resistance)
if support:
    untested_below[-1] = max(price for _, price in support)

for bar, price in resistance:
    line.new(x1=int(bar), y1=price, x2=min(n - 1, int(bar) + extend_bars), y2=price,
             color="#ef5350", width=1, style=line.style_dashed)
    if show_labels:
        label.new(x=min(n - 1, int(bar) + 2), y=price, text="untested",
                  style=label.style_label_left, color="rgba(239,83,80,0.15)",
                  textcolor="#ef5350", size="small")

for bar, price in support:
    line.new(x1=int(bar), y1=price, x2=min(n - 1, int(bar) + extend_bars), y2=price,
             color="#00e676", width=1, style=line.style_dashed)
    if show_labels:
        label.new(x=min(n - 1, int(bar) + 2), y=price, text="untested",
                  style=label.style_label_left, color="rgba(0,230,118,0.15)",
                  textcolor="#00e676", size="small")

plot(untested_above, title="Nearest untested resistance", color="red")
plot(untested_below, title="Nearest untested support", color="green")
