from tg_scripting import *
import numpy as np

indicator("Trend Follower Strategy", overlay=True)

atr_len = input.int(10, "ATR Length", minval=5, maxval=30)
base_mult = input.float(3.0, "Base Multiplier", minval=1.0, maxval=6.0, step=0.5)
tp_mult = input.float(3.0, "Take Profit ATR Mult", minval=1.5, maxval=6.0, step=0.5)

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

in_long = False
in_short = False
entry_price = 0.0
for i in range(1, n):
    strategy.set_bar_index(i)
    if trend[i] == 1 and trend[i-1] != 1:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price = float(cl[i])
    elif trend[i] == -1 and trend[i-1] != -1:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price = float(cl[i])

    if in_long:
        tp = entry_price + atr_arr[i] * tp_mult
        strategy.exit("Long", stop=float(trend_line[i]), limit=tp)
        if cl[i] <= trend_line[i] or cl[i] >= tp:
            in_long = False
    if in_short:
        tp = entry_price - atr_arr[i] * tp_mult
        strategy.exit("Short", stop=float(trend_line[i]), limit=tp)
        if cl[i] >= trend_line[i] or cl[i] <= tp:
            in_short = False

plot(trend_line.tolist(), title="Dynamic Trend", color="#ff9800", linewidth=2)
