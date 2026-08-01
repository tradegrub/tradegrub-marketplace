from tg_scripting import *
import numpy as np

indicator("Gann Square Levels", overlay=True)

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
levels_above = input.int(4, "Levels Above", minval=1, maxval=8)
levels_below = input.int(4, "Levels Below", minval=1, maxval=8)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

ref_high = np.array(ta.highest(high, lookback), dtype=float)
ref_low = np.array(ta.lowest(low, lookback), dtype=float)

# Degree increments: 90=0.25, 180=0.5, 270=0.75, 360=1.0
increments = []
for k in range(1, max(levels_above, levels_below) + 1):
    for step in [0.25, 0.5, 0.75, 1.0]:
        increments.append((k - 1) * 1.0 + step)

# Colors by degree within cycle
# 360 (1.0) = strong, 180 (0.5) = medium, 90/270 = light
def degree_color_above(inc):
    frac = inc % 1.0
    if abs(frac) < 0.01 or abs(frac - 1.0) < 0.01:
        return "#ff5252"  # 360 - strong red
    if abs(frac - 0.5) < 0.01:
        return "#ff8a80"  # 180 - medium red
    return "#ffcdd2"      # 90/270 - light red

def degree_color_below(inc):
    frac = inc % 1.0
    if abs(frac) < 0.01 or abs(frac - 1.0) < 0.01:
        return "#4CAF50"  # 360 - strong green
    if abs(frac - 0.5) < 0.01:
        return "#81C784"  # 180 - medium green
    return "#C8E6C9"      # 90/270 - light green

def degree_label(inc):
    deg = int((inc % 1.0) * 360)
    if deg == 0:
        deg = 360
    cycle = int(inc)
    if deg == 360:
        cycle = cycle  # full cycle completed
    return f"{deg}d c{cycle + 1}"

# Calculate levels above from ref_high
above_levels = []
for i in range(levels_above * 4):
    if i >= len(increments):
        break
    inc = increments[i]
    level = np.full(n, np.nan)
    for j in range(lookback, n):
        sqrt_ref = np.sqrt(ref_high[j])
        val = (sqrt_ref + inc) ** 2
        level[j] = val
    above_levels.append((level, inc))

# Calculate levels below from ref_low
below_levels = []
for i in range(levels_below * 4):
    if i >= len(increments):
        break
    inc = increments[i]
    level = np.full(n, np.nan)
    for j in range(lookback, n):
        sqrt_ref = np.sqrt(ref_low[j])
        val = (sqrt_ref - inc) ** 2
        if val > 0:
            level[j] = val
        else:
            level[j] = np.nan
    below_levels.append((level, inc))

# Plot levels above (resistance)
for level, inc in above_levels:
    lbl = f"R {degree_label(inc)}"
    clr = degree_color_above(inc)
    plot(level.tolist(), title=lbl, color=clr, linewidth=1)

# Plot levels below (support)
for level, inc in below_levels:
    lbl = f"S {degree_label(inc)}"
    clr = degree_color_below(inc)
    plot(level.tolist(), title=lbl, color=clr, linewidth=1)
