from tg_scripting import *
import numpy as np

indicator("RMI Band Reversal", overlay=False)

rmi_len = input.int(14, "RMI Length", minval=2, maxval=50)
momentum = input.int(5, "Momentum Period", minval=1, maxval=20)
bb_len = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0, step=0.5)

cl = np.array(close, dtype=np.float64)
n = len(cl)

rmi = np.full(n, 50.0)
if n > momentum + rmi_len:
    delta = np.zeros(n)
    for i in range(momentum, n):
        delta[i] = cl[i] - cl[i - momentum]

    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    start = momentum + rmi_len
    avg_gain = np.mean(gain[momentum:start])
    avg_loss = np.mean(loss[momentum:start])

    if avg_loss == 0:
        rmi[start - 1] = 100.0
    else:
        rmi[start - 1] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)

    for i in range(start, n):
        avg_gain = (avg_gain * (rmi_len - 1) + gain[i]) / rmi_len
        avg_loss = (avg_loss * (rmi_len - 1) + loss[i]) / rmi_len
        if avg_loss == 0:
            rmi[i] = 100.0
        else:
            rmi[i] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)

bb_mid = np.full(n, 50.0)
bb_upper = np.full(n, 70.0)
bb_lower = np.full(n, 30.0)

for i in range(bb_len - 1, n):
    window = rmi[i - bb_len + 1:i + 1]
    m = np.mean(window)
    s = np.std(window)
    bb_mid[i] = m
    bb_upper[i] = m + bb_mult * s
    bb_lower[i] = m - bb_mult * s

in_long = False
in_short = False

for i in range(1, n):
    if rmi[i] > bb_lower[i] and rmi[i - 1] <= bb_lower[i - 1] and rmi[i] < 40:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False

    if rmi[i] < bb_upper[i] and rmi[i - 1] >= bb_upper[i - 1] and rmi[i] > 60:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False

    if in_long and (rmi[i] > 60 or (rmi[i] > bb_mid[i] and rmi[i - 1] <= bb_mid[i - 1])):
        strategy.close("Long")
        in_long = False

    if in_short and (rmi[i] < 40 or (rmi[i] < bb_mid[i] and rmi[i - 1] >= bb_mid[i - 1])):
        strategy.close("Short")
        in_short = False

plot(rmi.tolist(), title="RMI", color="#2196F3", linewidth=2)
p_upper = plot(bb_upper.tolist(), title="BB Upper", color="#ef5350")
p_lower = plot(bb_lower.tolist(), title="BB Lower", color="#26a69a")
plot(bb_mid.tolist(), title="BB Mid", color="#FF9800")
fill(p_upper, p_lower, color="rgba(33,150,243,0.08)")
hline(60, title="Overbought", color="#ef5350", linestyle="dashed")
hline(40, title="Oversold", color="#26a69a", linestyle="dashed")
