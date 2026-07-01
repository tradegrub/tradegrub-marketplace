from tg_scripting import *
import numpy as np

indicator("Fisher Transform", overlay=False)

length = input.int(10, "Period", minval=2, maxval=50)
sig_len = input.int(3, "Signal Smoothing", minval=1, maxval=10)

n = len(close)
hl2 = (high + low) / 2.0
highest_hl = ta.highest(hl2, length)
lowest_hl = ta.lowest(hl2, length)

raw = np.full(n, 0.0)
fisher = np.full(n, 0.0)
prev_raw = 0.0
prev_fisher = 0.0

for i in range(length, n):
    rng = highest_hl[i] - lowest_hl[i]
    if rng > 0:
        val = 2.0 * ((hl2[i] - lowest_hl[i]) / rng) - 1.0
    else:
        val = 0.0
    # Clamp to avoid log domain error
    val = max(-0.999, min(0.999, val))
    # Smooth the normalized value
    raw[i] = 0.5 * val + 0.5 * prev_raw
    raw[i] = max(-0.999, min(0.999, raw[i]))
    fisher[i] = 0.5 * np.log((1.0 + raw[i]) / (1.0 - raw[i])) + 0.5 * prev_fisher
    prev_raw = raw[i]
    prev_fisher = fisher[i]

signal = np.roll(fisher, 1)
signal[0] = 0.0

bull_cross = np.full(n, False)
bear_cross = np.full(n, False)
for i in range(1, n):
    if fisher[i] > signal[i] and fisher[i - 1] <= signal[i - 1]:
        bull_cross[i] = True
    if fisher[i] < signal[i] and fisher[i - 1] >= signal[i - 1]:
        bear_cross[i] = True

plot(fisher, title="Fisher", color="#42A5F5", linewidth=2)
plot(signal, title="Trigger", color="#ff9800", linewidth=1)
hline(0.0, title="Zero", color="#666666", linestyle="dashed")
hline(1.5, title="Overbought", color="#ff5252", linestyle="dashed")
hline(-1.5, title="Oversold", color="#4CAF50", linestyle="dashed")

plotshape(bull_cross, title="Bull", shape="triangleup", location="bottom", color="#00e676", size="small")
plotshape(bear_cross, title="Bear", shape="triangledown", location="top", color="#ff1744", size="small")
