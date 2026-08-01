from tg_scripting import *
import numpy as np

indicator("Ergodic Oscillator", overlay=False)

long_len = input.int(25, "Long Period", minval=5, maxval=100)
short_len = input.int(13, "Short Period", minval=3, maxval=50)
sig_len = input.int(5, "Signal Length", minval=2, maxval=20)

n = len(close)
momentum = np.diff(close, prepend=close[0])

abs_mom = np.abs(momentum)

# Double smooth momentum
smooth1 = ta.ema(momentum, long_len)
smooth2 = ta.ema(smooth1, short_len)

# Double smooth absolute momentum
abs_smooth1 = ta.ema(abs_mom, long_len)
abs_smooth2 = ta.ema(abs_smooth1, short_len)

# TSI = 100 * double_smooth(mom) / double_smooth(abs_mom)
tsi = np.where(abs_smooth2 != 0, 100.0 * smooth2 / abs_smooth2, 0.0)
signal = ta.ema(tsi, sig_len)
hist = tsi - signal

bull_cross = np.full(n, False)
bear_cross = np.full(n, False)
for i in range(1, n):
    if tsi[i] > signal[i] and tsi[i - 1] <= signal[i - 1]:
        bull_cross[i] = True
    if tsi[i] < signal[i] and tsi[i - 1] >= signal[i - 1]:
        bear_cross[i] = True

plot(tsi, title="Ergodic", color="#42A5F5", linewidth=2)
plot(signal, title="Signal", color="#ff9800", linewidth=1)
plot(hist, title="Histogram", color="#7E57C2", style="histogram")
hline(0.0, title="Zero", color="#666666", linestyle="dashed")

plotshape(bull_cross, title="Bull Cross", shape="triangleup", location="bottom", color="#00e676", size="small")
plotshape(bear_cross, title="Bear Cross", shape="triangledown", location="top", color="#ff1744", size="small")
