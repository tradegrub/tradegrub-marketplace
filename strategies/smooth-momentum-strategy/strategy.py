from tg_scripting import *
import numpy as np

indicator("Smooth Momentum Strategy", overlay=True)

mom_len = input.int(14, "Momentum Length", minval=5, maxval=30)
smooth_stages = input.int(3, "Smoothing Stages", minval=1, maxval=5)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
stop_mult = input.float(2.0, "Stop ATR Mult", minval=1.0, maxval=4.0, step=0.5)
tp_mult = input.float(3.0, "TP ATR Mult", minval=1.5, maxval=6.0, step=0.5)

cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

momentum = np.zeros(n)
for i in range(mom_len, n):
    momentum[i] = (cl[i] - cl[i-mom_len]) / max(cl[i-mom_len], 1e-10) * 100

smooth_mom = np.copy(momentum)
alpha = 2.0 / (mom_len / 2 + 1)
for _ in range(smooth_stages):
    temp = np.copy(smooth_mom)
    for i in range(1, n):
        temp[i] = alpha * smooth_mom[i] + (1 - alpha) * temp[i-1]
    smooth_mom = temp

slope = np.zeros(n)
for i in range(3, n):
    slope[i] = smooth_mom[i] - smooth_mom[i-3]

long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
for i in range(1, n):
    if smooth_mom[i] > 0 and smooth_mom[i-1] <= 0 and slope[i] > 0:
        long_sig[i] = True
    elif smooth_mom[i] < 0 and smooth_mom[i-1] >= 0 and slope[i] < 0:
        short_sig[i] = True

in_long = False
in_short = False
entry_price = 0.0
for i in range(mom_len, n):
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
