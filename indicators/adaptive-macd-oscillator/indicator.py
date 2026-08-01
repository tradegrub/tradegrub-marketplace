from tg_scripting import *
import numpy as np

indicator("Adaptive MACD Oscillator", overlay=False)

fast_len = input.int(12, "Fast Length", minval=5, maxval=30)
slow_len = input.int(26, "Slow Length", minval=15, maxval=60)
signal_len = input.int(9, "Signal Length", minval=3, maxval=20)

src = np.array(close, dtype=float)
n = len(src)

def adaptive_ema(data, length):
    out = np.copy(data)
    for i in range(1, len(data)):
        mom = abs(data[i] - data[max(0, i-length)]) if i >= length else 0
        vol = sum(abs(data[j] - data[j-1]) for j in range(max(1, i-length+1), i+1))
        er = mom / max(vol, 1e-10)
        fast_sc = 2.0 / 3.0
        slow_sc = 2.0 / (length + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        out[i] = sc * data[i] + (1 - sc) * out[i-1]
    return out

fast_ma = adaptive_ema(src, fast_len)
slow_ma = adaptive_ema(src, slow_len)
macd_line = fast_ma - slow_ma

signal = np.zeros(n)
alpha = 2.0 / (signal_len + 1)
for i in range(1, n):
    signal[i] = alpha * macd_line[i] + (1 - alpha) * signal[i-1]

histogram = macd_line - signal

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if macd_line[i] > signal[i] and macd_line[i-1] <= signal[i-1]:
        cross_up[i] = True
    elif macd_line[i] < signal[i] and macd_line[i-1] >= signal[i-1]:
        cross_down[i] = True

plot(macd_line.tolist(), title="MACD", color="#26c6da", linewidth=2)
plot(signal.tolist(), title="Signal", color="#ff9800", linewidth=1)
plot(histogram.tolist(), title="Histogram", color="#78909C", style=plot.style_histogram)
hline(0, title="Zero", color="#888888", linestyle="dashed")
plotshape(cross_up.tolist(), title="Bull Cross", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Bear Cross", style="triangledown", location="abovebar", color="#ff1744", size="small")
