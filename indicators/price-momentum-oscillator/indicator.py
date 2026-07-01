from tg_scripting import *
import numpy as np

indicator("Price Momentum Oscillator", overlay=False)

roc_len = input.int(1, "ROC Period", minval=1, maxval=10)
smooth1 = input.int(35, "First Smoothing", minval=5, maxval=100)
smooth2 = input.int(20, "Second Smoothing", minval=5, maxval=100)
sig_len = input.int(10, "Signal Length", minval=3, maxval=30)

n = len(close)
roc = np.full(n, 0.0)
for i in range(roc_len, n):
    if close[i - roc_len] != 0:
        roc[i] = ((close[i] - close[i - roc_len]) / close[i - roc_len]) * 100.0

first_smooth = ta.ema(roc, smooth1)
pmo = ta.ema(first_smooth, smooth2)
signal = ta.ema(pmo, sig_len)
hist = pmo - signal

bull_cross = np.full(n, False)
bear_cross = np.full(n, False)
for i in range(1, n):
    if pmo[i] > signal[i] and pmo[i - 1] <= signal[i - 1]:
        bull_cross[i] = True
    if pmo[i] < signal[i] and pmo[i - 1] >= signal[i - 1]:
        bear_cross[i] = True

plot(pmo, title="PMO", color="#42A5F5", linewidth=2)
plot(signal, title="Signal", color="#ff9800", linewidth=1)
plot(hist, title="Histogram", color="#7E57C2", style="histogram")
hline(0.0, title="Zero", color="#666666", linestyle="dashed")

plotshape(bull_cross, title="Bull Cross", shape="triangleup", location="bottom", color="#00e676", size="small")
plotshape(bear_cross, title="Bear Cross", shape="triangledown", location="top", color="#ff1744", size="small")
