from tg_scripting import *
import numpy as np

indicator("Adaptive Stop and Reverse", overlay=True)

af_start = input.float(0.02, "AF Start", minval=0.01, maxval=0.1, step=0.01)
af_max = input.float(0.2, "AF Max", minval=0.1, maxval=0.5, step=0.05)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

atr_pct = np.zeros(n)
for i in range(50, n):
    window = atr_arr[i-50:i]
    atr_pct[i] = np.sum(window <= atr_arr[i]) / 50

sar = np.zeros(n)
is_long = True
ep = hi[0]
af = af_start
sar[0] = lo[0]

for i in range(1, n):
    vol_adj = 0.5 + atr_pct[i]
    cur_af_max = af_max * vol_adj

    if is_long:
        sar[i] = sar[i-1] + af * (ep - sar[i-1])
        sar[i] = min(sar[i], lo[i-1])
        if i >= 2:
            sar[i] = min(sar[i], lo[i-2])
        if hi[i] > ep:
            ep = hi[i]
            af = min(af + af_start, cur_af_max)
        if lo[i] < sar[i]:
            is_long = False
            sar[i] = ep
            ep = lo[i]
            af = af_start
    else:
        sar[i] = sar[i-1] + af * (ep - sar[i-1])
        sar[i] = max(sar[i], hi[i-1])
        if i >= 2:
            sar[i] = max(sar[i], hi[i-2])
        if lo[i] < ep:
            ep = lo[i]
            af = min(af + af_start, cur_af_max)
        if hi[i] > sar[i]:
            is_long = True
            sar[i] = ep
            ep = hi[i]
            af = af_start


plot(sar.tolist(), title="Adaptive SAR", color="#ff9800", linewidth=1)
