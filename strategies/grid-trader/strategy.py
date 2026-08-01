from tg_scripting import *
import numpy as np

indicator("Grid Level Trader", overlay=True)

grid_spacing = input.float(2.0, "Grid Spacing (%)", minval=0.1, maxval=10.0, step=0.5)
num_grids = input.int(5, "Number of Grid Levels", minval=1, maxval=20)
sma_len = input.int(50, "SMA Length", minval=5, maxval=200)
use_atr = input.bool(False, "Use ATR for Spacing")

c = np.array(close, dtype=np.float64)
h = np.array(high, dtype=np.float64)
l = np.array(low, dtype=np.float64)
n = len(c)

ref = np.array(ta.sma(close, sma_len), dtype=np.float64)
atr_vals = np.array(ta.atr(high, low, close, 14), dtype=np.float64)

plot(ref.tolist(), title="Reference SMA", color="#2196F3", linewidth=2)

in_position = False

for i in range(sma_len, n):
    strategy.set_bar_index(i)
    if np.isnan(ref[i]):
        continue

    if use_atr and not np.isnan(atr_vals[i]):
        spacing = atr_vals[i]
    else:
        spacing = ref[i] * (grid_spacing / 100.0)

    for g in range(1, num_grids + 1):
        buy_level = ref[i] - g * spacing
        sell_level = ref[i] + g * spacing

        if not in_position and c[i] <= buy_level and c[i - 1] > buy_level:
            strategy.entry("Long", strategy.LONG)
            in_position = True
            label.new(x=i, y=float(c[i]), text="BUY",
                      style=label.style_label_up, color="#26a69a",
                      textcolor="#ffffff", size="tiny")
            break

        if in_position and c[i] >= sell_level and c[i - 1] < sell_level:
            strategy.close("Long")
            in_position = False
            label.new(x=i, y=float(c[i]), text="SELL",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="tiny")
            break
