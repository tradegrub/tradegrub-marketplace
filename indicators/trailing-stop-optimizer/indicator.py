from tg_scripting import *
import numpy as np

indicator("Trailing Stop Optimizer", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(3.0, "ATR Multiplier", minval=1.0, maxval=6.0, step=0.5)
pct_stop = input.float(2.0, "Percent Stop %", minval=0.5, maxval=10.0, step=0.5)
show_chandelier = input.bool(True, "Show Chandelier Stop")

n = len(close)
atr = ta.atr(high, low, close, atr_len)

atr_trail = np.full(n, np.nan)
pct_trail = np.full(n, np.nan)
chand_trail = np.full(n, np.nan)
best_stop = np.full(n, np.nan)

highest_close = np.zeros(n)
highest_close[0] = close[0]

for i in range(1, n):
    if close[i] > highest_close[i - 1]:
        highest_close[i] = close[i]
    else:
        highest_close[i] = highest_close[i - 1]

    if not np.isnan(atr[i]):
        atr_trail[i] = highest_close[i] - atr[i] * atr_mult

    pct_trail[i] = highest_close[i] * (1.0 - pct_stop / 100.0)

hi_arr = ta.highest(high, atr_len)
for i in range(n):
    if not np.isnan(hi_arr[i]) and not np.isnan(atr[i]):
        chand_trail[i] = hi_arr[i] - atr[i] * atr_mult

for i in range(n):
    stops = []
    if not np.isnan(atr_trail[i]):
        stops.append(atr_trail[i])
    if not np.isnan(pct_trail[i]):
        stops.append(pct_trail[i])
    if show_chandelier and not np.isnan(chand_trail[i]):
        stops.append(chand_trail[i])
    if stops:
        best_stop[i] = max(stops)

plot(atr_trail, title="ATR Trail", color="#42a5f5", linewidth=1)
plot(pct_trail, title="Percent Trail", color="#ffa726", linewidth=1)
if show_chandelier:
    plot(chand_trail, title="Chandelier", color="#ab47bc", linewidth=1)
plot(best_stop, title="Best Stop", color="#00e676", linewidth=2)

stopped = np.array([close[i] < best_stop[i] if not np.isnan(best_stop[i]) else False for i in range(n)], dtype=bool)
plotshape(stopped, title="Stop Hit", style="triangledown", location="abovebar", color="#ff5252")
