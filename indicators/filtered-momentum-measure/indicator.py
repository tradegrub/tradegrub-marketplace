from tg_scripting import *
import numpy as np

indicator("Filtered Momentum Measure", overlay=False)

length = input.int(14, "Momentum Length", minval=5, maxval=50)
smooth_len = input.int(8, "Smoothing Length", minval=3, maxval=30)
signal_len = input.int(5, "Signal Length", minval=2, maxval=15)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

atr_arr = np.array(ta.atr(high, low, close, length), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

smoothed = np.copy(src)
for i in range(1, n):
    vol_ratio = atr_arr[i] / max(np.mean(atr_arr[max(0,i-50):i+1]), 1e-10)
    alpha = 2.0 / (smooth_len * max(vol_ratio, 0.5) + 1)
    alpha = np.clip(alpha, 0.01, 0.5)
    smoothed[i] = alpha * src[i] + (1 - alpha) * smoothed[i-1]

momentum = np.zeros(n)
for i in range(length, n):
    momentum[i] = (smoothed[i] - smoothed[i - length]) / max(smoothed[i - length], 1e-10) * 100

signal = np.array(ta.sma(momentum.tolist(), signal_len), dtype=float)
signal = np.nan_to_num(signal, nan=0.0)

hist = momentum - signal

plot(momentum.tolist(), title="Filtered Momentum", color="#26c6da", linewidth=2)
plot(signal.tolist(), title="Signal", color="#ff9800", linewidth=1)
plot(hist.tolist(), title="Histogram", color="#78909C", style=plot.style_histogram)
hline(0, title="Zero", color="#888888", linestyle="dashed")
