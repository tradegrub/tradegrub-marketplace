from tg_scripting import *
import numpy as np

indicator("Directional Vortex Strategy", overlay=True)

length = input.int(14, "Vortex Length", minval=5, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
stop_mult = input.float(2.0, "Stop ATR Mult", minval=1.0, maxval=4.0, step=0.5)
tp_mult = input.float(3.0, "TP ATR Mult", minval=1.5, maxval=6.0, step=0.5)
threshold = input.float(0.1, "Cross Threshold", minval=0.02, maxval=0.3, step=0.02)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

vm_p = np.zeros(n)
vm_m = np.zeros(n)
tr_arr = np.zeros(n)
for i in range(1, n):
    vm_p[i] = abs(hi[i] - lo[i-1])
    vm_m[i] = abs(lo[i] - hi[i-1])
    tr_arr[i] = max(hi[i] - lo[i], abs(hi[i] - cl[i-1]), abs(lo[i] - cl[i-1]))

vi_p = np.zeros(n)
vi_m = np.zeros(n)
for i in range(length, n):
    tr_sum = np.sum(tr_arr[i-length+1:i+1])
    if tr_sum > 0:
        vi_p[i] = np.sum(vm_p[i-length+1:i+1]) / tr_sum
        vi_m[i] = np.sum(vm_m[i-length+1:i+1]) / tr_sum

long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
for i in range(1, n):
    diff = vi_p[i] - vi_m[i]
    prev_diff = vi_p[i-1] - vi_m[i-1]
    if diff > threshold and prev_diff <= threshold:
        long_sig[i] = True
    elif diff < -threshold and prev_diff >= -threshold:
        short_sig[i] = True

in_long = False
in_short = False
entry_price = 0.0
for i in range(length, n):
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
        tp = entry_price + atr_arr[i] * tp_mult
        strategy.exit("Long", stop=sl, limit=tp)
        if cl[i] <= sl or cl[i] >= tp:
            in_long = False
    if in_short:
        sl = entry_price + atr_arr[i] * stop_mult
        tp = entry_price - atr_arr[i] * tp_mult
        strategy.exit("Short", stop=sl, limit=tp)
        if cl[i] >= sl or cl[i] <= tp:
            in_short = False

plotshape(long_sig.tolist(), title="Long", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(short_sig.tolist(), title="Short", style="triangledown", location="abovebar", color="#ff1744", size="small")
