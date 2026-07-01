from tg_scripting import *
import numpy as np

indicator("Chande Momentum Oscillator", overlay=False)

length = input.int(14, "Period", minval=2, maxval=100)
overbought = input.float(50.0, "Overbought", minval=20.0, maxval=80.0)
oversold = input.float(-50.0, "Oversold", minval=-80.0, maxval=-20.0)
sig_len = input.int(9, "Signal Length", minval=2, maxval=30)

n = len(close)
up_sum = np.full(n, 0.0)
down_sum = np.full(n, 0.0)

for i in range(length, n):
    u = 0.0
    d = 0.0
    for j in range(i - length + 1, i + 1):
        diff = close[j] - close[j - 1]
        if diff > 0:
            u += diff
        else:
            d += abs(diff)
    up_sum[i] = u
    down_sum[i] = d

total = up_sum + down_sum
cmo = np.where(total != 0, 100.0 * (up_sum - down_sum) / total, 0.0)
signal = ta.ema(cmo, sig_len)


plot(cmo, title="CMO", color="#42A5F5", linewidth=2)
plot(signal, title="Signal", color="#ff9800", linewidth=1)
hline(overbought, title="Overbought", color="#4CAF50", linestyle="dashed")
hline(oversold, title="Oversold", color="#ff5252", linestyle="dashed")
hline(0.0, title="Zero", color="#666666", linestyle="dashed")

