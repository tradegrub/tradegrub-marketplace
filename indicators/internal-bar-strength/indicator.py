from tg_scripting import *
import numpy as np

indicator("Internal Bar Strength", overlay=False)

length = input.int(14, "Smoothing Length", minval=3, maxval=50)
signal_len = input.int(5, "Signal Length", minval=2, maxval=15)
use_adaptive = input.bool(True, "Adaptive Scaling")

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

ibs = np.zeros(n)
for i in range(n):
    rng = hi[i] - lo[i]
    if rng > 0:
        ibs[i] = (cl[i] - lo[i]) / rng * 100

bsi = np.array(ta.sma(ibs.tolist(), length), dtype=float)
bsi = np.nan_to_num(bsi, nan=50.0)

if use_adaptive:
    for i in range(50, n):
        window = bsi[i-50:i]
        mu = np.mean(window)
        std = np.std(window)
        if std > 0:
            bsi[i] = 50 + (bsi[i] - mu) / std * 15

signal = np.array(ta.ema(bsi.tolist(), signal_len), dtype=float)
signal = np.nan_to_num(signal, nan=50.0)

ob = bsi > 70
os_zone = bsi < 30

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if bsi[i] > signal[i] and bsi[i-1] <= signal[i-1]:
        cross_up[i] = True
    elif bsi[i] < signal[i] and bsi[i-1] >= signal[i-1]:
        cross_down[i] = True

plot(bsi.tolist(), title="Bar Strength", color="#42a5f5", linewidth=2)
plot(signal.tolist(), title="Signal", color="#ff9800", linewidth=1)
hline(70, title="Overbought", color="#f44336", linestyle="dashed")
hline(30, title="Oversold", color="#4CAF50", linestyle="dashed")
hline(50, title="Mid", color="#888888", linestyle="dashed")
bgcolor(ob.tolist(), color="rgba(244,67,54,0.06)")
bgcolor(os_zone.tolist(), color="rgba(76,175,80,0.06)")
plotshape(cross_up.tolist(), title="Bull Cross", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Bear Cross", style="triangledown", location="abovebar", color="#ff1744", size="small")
