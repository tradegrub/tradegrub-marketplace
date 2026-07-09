from tg_scripting import *
import numpy as np

indicator("Trend Emergence Strategy", overlay=True)

aroon_len = input.int(25, "Aroon Length", minval=10, maxval=60)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
stop_mult = input.float(2.0, "Stop ATR Mult", minval=1.0, maxval=4.0, step=0.5)
tp_mult = input.float(3.0, "TP ATR Mult", minval=1.5, maxval=6.0, step=0.5)
aroon_thresh = input.int(70, "Aroon Threshold", minval=50, maxval=90)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

aroon_up = np.zeros(n)
aroon_down = np.zeros(n)
for i in range(aroon_len, n):
    hh = np.argmax(hi[i-aroon_len:i+1])
    ll = np.argmin(lo[i-aroon_len:i+1])
    aroon_up[i] = hh / aroon_len * 100
    aroon_down[i] = ll / aroon_len * 100

long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
for i in range(1, n):
    if aroon_up[i] > aroon_thresh and aroon_up[i-1] <= aroon_thresh and aroon_up[i] > aroon_down[i]:
        long_sig[i] = True
    if aroon_down[i] > aroon_thresh and aroon_down[i-1] <= aroon_thresh and aroon_down[i] > aroon_up[i]:
        short_sig[i] = True

in_long = False
in_short = False
entry_price = 0.0
for i in range(aroon_len, n):
    strategy.set_bar_index(i)
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
