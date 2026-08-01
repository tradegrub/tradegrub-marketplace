from tg_scripting import *
import numpy as np

indicator("Dynamic Trend Follower", overlay=True)

atr_len = input.int(10, "ATR Length", minval=5, maxval=30)
base_mult = input.float(3.0, "Base Multiplier", minval=1.0, maxval=6.0, step=0.5)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

dyn_mult = np.full(n, base_mult)
for i in range(50, n):
    atr_window = atr_arr[i-50:i]
    pct = np.sum(atr_window <= atr_arr[i]) / 50
    dyn_mult[i] = base_mult * (0.7 + 0.6 * pct)

mid = (hi + lo) / 2
upper = mid + dyn_mult * atr_arr
lower = mid - dyn_mult * atr_arr

trend = np.zeros(n)
trend_line = np.zeros(n)
trend_line[0] = cl[0]

for i in range(1, n):
    if cl[i] > upper[i-1]:
        trend[i] = 1
    elif cl[i] < lower[i-1]:
        trend[i] = -1
    else:
        trend[i] = trend[i-1]

    if trend[i] == 1:
        trend_line[i] = max(lower[i], trend_line[i-1] if trend[i-1] == 1 else lower[i])
    else:
        trend_line[i] = min(upper[i], trend_line[i-1] if trend[i-1] == -1 else upper[i])


plot(trend_line.tolist(), title="Dynamic Trend", color="#ff9800", linewidth=2)
