from tg_scripting import *
import numpy as np
from scipy.optimize import minimize_scalar

indicator("Optimized Crossover Strategy", overlay=True)

train_window = input.int(100, "Training Window", minval=50, maxval=200)
reopt_period = input.int(50, "Re-optimize Every", minval=20, maxval=100)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
stop_mult = input.float(2.0, "Stop ATR Mult", minval=1.0, maxval=4.0, step=0.5)

cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

def eval_crossover(fast_len, data):
    fast_len = max(3, int(fast_len))
    slow_len = fast_len * 3
    if slow_len >= len(data):
        return 0
    fast_ma = np.convolve(data, np.ones(fast_len)/fast_len, mode='valid')
    slow_ma = np.convolve(data, np.ones(slow_len)/slow_len, mode='valid')
    min_len = min(len(fast_ma), len(slow_ma))
    fast_ma = fast_ma[-min_len:]
    slow_ma = slow_ma[-min_len:]
    data_slice = data[-min_len:]
    pnl = 0
    pos = 0
    for i in range(1, min_len):
        if fast_ma[i] > slow_ma[i] and fast_ma[i-1] <= slow_ma[i-1]:
            pos = 1
        elif fast_ma[i] < slow_ma[i] and fast_ma[i-1] >= slow_ma[i-1]:
            pos = -1
        if i > 0:
            pnl += pos * (data_slice[i] - data_slice[i-1])
    return -pnl

opt_fast = 10
opt_slow = 30
next_opt = train_window

fast_ma_arr = np.array(ta.sma(close, 10), dtype=float)
slow_ma_arr = np.array(ta.sma(close, 30), dtype=float)
fast_ma_arr = np.nan_to_num(fast_ma_arr, nan=0.0)
slow_ma_arr = np.nan_to_num(slow_ma_arr, nan=0.0)

for i in range(train_window, n):
    if i >= next_opt:
        train_data = cl[i-train_window:i]
        try:
            result = minimize_scalar(eval_crossover, bounds=(3, 30), args=(train_data,), method='bounded')
            opt_fast = max(3, int(result.x))
            opt_slow = opt_fast * 3
        except Exception:
            pass
        next_opt = i + reopt_period
        fast_ma_arr = np.array(ta.sma(close, opt_fast), dtype=float)
        slow_ma_arr = np.array(ta.sma(close, opt_slow), dtype=float)
        fast_ma_arr = np.nan_to_num(fast_ma_arr, nan=0.0)
        slow_ma_arr = np.nan_to_num(slow_ma_arr, nan=0.0)

long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
for i in range(1, n):
    if fast_ma_arr[i] > slow_ma_arr[i] and fast_ma_arr[i-1] <= slow_ma_arr[i-1]:
        long_sig[i] = True
    elif fast_ma_arr[i] < slow_ma_arr[i] and fast_ma_arr[i-1] >= slow_ma_arr[i-1]:
        short_sig[i] = True

in_long = False
in_short = False
entry_price = 0.0
for i in range(train_window, n):
    if long_sig[i] and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price = float(cl[i])
    elif short_sig[i] and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price = float(cl[i])

    if in_long:
        sl = entry_price - atr_arr[i] * stop_mult
        strategy.exit("Long", stop=sl)
        if cl[i] <= sl:
            in_long = False
    if in_short:
        sl = entry_price + atr_arr[i] * stop_mult
        strategy.exit("Short", stop=sl)
        if cl[i] >= sl:
            in_short = False

plot(fast_ma_arr.tolist(), title="Fast MA", color="#26c6da", linewidth=1)
plot(slow_ma_arr.tolist(), title="Slow MA", color="#ef5350", linewidth=1)
plotshape(long_sig.tolist(), title="Long", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(short_sig.tolist(), title="Short", style="triangledown", location="abovebar", color="#ff1744", size="small")
