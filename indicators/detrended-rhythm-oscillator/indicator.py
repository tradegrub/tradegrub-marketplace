from tg_scripting import *
import numpy as np

indicator("Detrended Rhythm Oscillator", overlay=False)

detrend_length = input.int(50, "Detrend Length", minval=10, maxval=200)
max_cycle = input.int(40, "Max Cycle", minval=5, maxval=100)

cl = np.array(close, dtype=float)
n = len(cl)

sma_arr = np.array(ta.sma(close, detrend_length), dtype=float)
sma_arr = np.nan_to_num(sma_arr, nan=0.0)
detrended = cl - sma_arr

autocorr = np.zeros(max_cycle + 1)
valid_start = detrend_length + max_cycle
if valid_start < n:
    segment = detrended[detrend_length:]
    segment_mean = np.mean(segment)
    segment_centered = segment - segment_mean
    var = np.sum(segment_centered ** 2)
    if var > 0:
        for lag in range(1, max_cycle + 1):
            if lag < len(segment_centered):
                autocorr[lag] = np.sum(segment_centered[lag:] * segment_centered[:-lag]) / var

best_lag = max(np.argmax(autocorr[2:]) + 2, 2) if len(autocorr) > 2 else 2
dominant_cycle = int(best_lag)

cycle_osc = np.zeros(n)
for i in range(dominant_cycle, n):
    window = detrended[i - dominant_cycle:i]
    if np.std(window) > 0:
        cycle_osc[i] = (detrended[i] - np.mean(window)) / np.std(window)

smoothed = np.copy(cycle_osc)
alpha = 2.0 / (max(dominant_cycle // 4, 2) + 1)
for i in range(1, n):
    smoothed[i] = alpha * cycle_osc[i] + (1 - alpha) * smoothed[i - 1]

peaks = np.zeros(n, dtype=bool)
troughs = np.zeros(n, dtype=bool)
for i in range(1, n - 1):
    if smoothed[i] > smoothed[i - 1] and smoothed[i] > smoothed[i + 1] and smoothed[i] > 0.5:
        peaks[i] = True
    elif smoothed[i] < smoothed[i - 1] and smoothed[i] < smoothed[i + 1] and smoothed[i] < -0.5:
        troughs[i] = True

plot(smoothed.tolist(), title="Rhythm Oscillator", color="#26c6da", linewidth=2)
plot(detrended.tolist(), title="Detrended Price", color="#888888", linewidth=1)
hline(0, title="Zero", color="#555555", linestyle="dashed")
hline(1.5, title="Upper", color="#f44336", linestyle="dashed")
hline(-1.5, title="Lower", color="#4CAF50", linestyle="dashed")
plotshape(peaks.tolist(), title="Cycle Peak", style="triangledown", location="abovebar", color="#ff1744", size="small")
plotshape(troughs.tolist(), title="Cycle Trough", style="triangleup", location="belowbar", color="#00e676", size="small")
