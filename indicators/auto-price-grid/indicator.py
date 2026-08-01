from tg_scripting import *
import numpy as np

indicator("Auto Price Grid", overlay=True)

lookback = input.int(100, "Lookback Period", minval=20, maxval=500)
num_levels = input.int(10, "Grid Levels", minval=3, maxval=20)
show_prices = input.bool(True, "Show Prices")

c = np.array(close, dtype=np.float64)
h = np.array(high, dtype=np.float64)
l = np.array(low, dtype=np.float64)
n = len(c)

period_high = float(np.nanmax(h[-lookback:])) if n >= lookback else float(np.nanmax(h))
period_low = float(np.nanmin(l[-lookback:])) if n >= lookback else float(np.nanmin(l))

step = (period_high - period_low) / num_levels

for i in range(num_levels + 1):
    level = period_low + step * i
    start_bar = max(0, n - lookback)
    line.new(x1=start_bar, y1=level, x2=n - 1, y2=level,
             color="#787b86", width=1, style=line.style_dotted)
    if show_prices:
        label.new(x=n - 1, y=level, text=f"{level:.2f}",
                  style=label.style_none, textcolor="#787b86", size="tiny")

current_zone = np.full(n, 0.0)
for i in range(n):
    for j in range(num_levels):
        zone_low = period_low + step * j
        zone_high = period_low + step * (j + 1)
        if c[i] >= zone_low and c[i] < zone_high:
            current_zone[i] = 1.0
            break

bgcolor(current_zone > 0, color="rgba(33,150,243,0.05)")
