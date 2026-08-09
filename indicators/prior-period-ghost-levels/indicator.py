# Prior Period Ghost Levels — old structure, kept faint, projected forward.
from tg_scripting import *
import numpy as np

indicator("Prior Period Ghost Levels", overlay=True)

period_bars = input.int(120, "Period length (bars)", minval=10, maxval=1000)
periods_back = input.int(2, "Periods back to ghost", minval=1, maxval=6)
show_mid = input.bool(True, "Show each period midpoint")

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
n = len(c)

ghost_high = np.full(n, np.nan)
ghost_low = np.full(n, np.nan)
ghost_mid = np.full(n, np.nan)

# Walk completed periods backwards from the most recent boundary. Each one is
# projected across the CURRENT period, which is what makes it a ghost: the
# level belongs to a period that has already finished.
last_boundary = (n // period_bars) * period_bars
drawn = 0

for k in range(1, periods_back + 1):
    end = last_boundary - (k - 1) * period_bars
    start = end - period_bars
    if start < 0:
        break

    seg_h, seg_l = h[start:end], l[start:end]
    if not (np.isfinite(seg_h).any() and np.isfinite(seg_l).any()):
        continue

    hi = float(np.nanmax(seg_h))
    lo = float(np.nanmin(seg_l))
    mid = (hi + lo) / 2.0
    fade = max(0.12, 0.55 - 0.12 * (k - 1))

    line.new(x1=int(end), y1=hi, x2=n - 1, y2=hi,
             color=f"rgba(239,83,80,{fade:.2f})", width=1, style=line.style_dashed)
    line.new(x1=int(end), y1=lo, x2=n - 1, y2=lo,
             color=f"rgba(0,230,118,{fade:.2f})", width=1, style=line.style_dashed)
    if show_mid:
        line.new(x1=int(end), y1=mid, x2=n - 1, y2=mid,
                 color=f"rgba(120,123,134,{fade:.2f})", width=1, style=line.style_dotted)

    label.new(x=int(end) + 2, y=hi, text=f"P-{k} high", style=label.style_label_left,
              color="rgba(239,83,80,0.12)", textcolor="#ef5350", size="small")

    if drawn == 0:
        ghost_high[end:] = hi
        ghost_low[end:] = lo
        ghost_mid[end:] = mid
    drawn += 1

plot(ghost_high, title="Prior period high", color="rgba(239,83,80,0.7)")
plot(ghost_low, title="Prior period low", color="rgba(0,230,118,0.7)")
if show_mid:
    plot(ghost_mid, title="Prior period midpoint", color="rgba(120,123,134,0.7)")
