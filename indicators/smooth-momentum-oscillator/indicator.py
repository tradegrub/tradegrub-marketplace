from tg_scripting import *
import numpy as np

indicator("Smooth Momentum Oscillator", overlay=False)

length = input.int(14, "Momentum Length", minval=5, maxval=50)
smooth_stages = input.int(3, "Smoothing Stages", minval=1, maxval=5)
signal_len = input.int(5, "Signal Length", minval=2, maxval=15)

cl = np.array(close, dtype=float)
n = len(cl)

raw_mom = np.zeros(n)
for i in range(length, n):
    raw_mom[i] = (cl[i] - cl[i-length]) / max(cl[i-length], 1e-10) * 100

smooth_mom = np.copy(raw_mom)
alpha = 2.0 / (length / 2 + 1)
for _ in range(smooth_stages):
    temp = np.copy(smooth_mom)
    for i in range(1, n):
        temp[i] = alpha * smooth_mom[i] + (1 - alpha) * temp[i-1]
    smooth_mom = temp

signal = np.array(ta.sma(smooth_mom.tolist(), signal_len), dtype=float)
signal = np.nan_to_num(signal, nan=0.0)

histogram = smooth_mom - signal

plot(smooth_mom.tolist(), title="Smooth Momentum", color="#2196F3", linewidth=2)
plot(signal.tolist(), title="Signal", color="#FF9800", linewidth=1)
plot(histogram.tolist(), title="Histogram", color="#78909C", style=plot.style_histogram)
hline(0, title="Zero", color="#888888", linestyle="dashed")
