from tg_scripting import *
import numpy as np

length = input.int(20, "Length", minval=2, maxval=200)
signal_length = input.int(9, "Signal Length", minval=2, maxval=50)

src = np.array(close, dtype=float)
n = len(src)

# Logarithmic weights: log(i+1) for i in range(length)
raw_weights = np.log(np.arange(1, length + 1, dtype=float) + 1.0)
weights = raw_weights / np.sum(raw_weights)

# Apply weighted average using numpy convolution
lma = np.full(n, np.nan)
for i in range(length - 1, n):
    window = src[i - length + 1:i + 1]
    lma[i] = float(np.dot(weights, window))

# Signal line: SMA of LMA
lma_list = lma.tolist()
signal = np.array(ta.sma(lma_list, signal_length), dtype=float)

plot(lma_list, title="LMA", color=color.blue)
plot(signal.tolist(), title="Signal", color=color.orange)

# Cross signals
cross_above = np.zeros(n, dtype=bool)
cross_below = np.zeros(n, dtype=bool)
valid = ~np.isnan(lma) & ~np.isnan(signal)
for i in range(1, n):
    if valid[i] & valid[i - 1]:
        cross_above[i] = (lma[i] > signal[i]) & (lma[i - 1] <= signal[i - 1])
        cross_below[i] = (lma[i] < signal[i]) & (lma[i - 1] >= signal[i - 1])

plotshape(cross_above, title="Bullish Cross", style="triangleup", location="belowbar", color=color.green)
plotshape(cross_below, title="Bearish Cross", style="triangledown", location="abovebar", color=color.red)
