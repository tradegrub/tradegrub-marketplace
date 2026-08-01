from tg_scripting import *
import numpy as np

indicator("Dominant Cycle Length", overlay=False)

max_period = input.int(60, "Max Period", minval=20, maxval=120)

cl = np.array(close, dtype=float)
n = len(cl)

cycle_length = np.zeros(n)
phase = np.zeros(n)

for i in range(max_period + 10, n):
    window = cl[i - max_period - 10:i + 1]
    # Detrend with linear regression
    x_axis = np.arange(len(window), dtype=float)
    coeffs = np.polyfit(x_axis, window, 1)
    detrended = window - np.polyval(coeffs, x_axis)

    # Normalize
    std_val = np.std(detrended)
    if std_val > 1e-10:
        detrended = detrended / std_val

    # Autocorrelation at lags 5 to max_period
    best_lag = 5
    best_corr = -1.0
    mean_d = np.mean(detrended)
    centered = detrended - mean_d
    var_d = np.sum(centered ** 2)

    if var_d > 1e-10:
        for lag in range(5, min(max_period + 1, len(centered))):
            corr = np.sum(centered[:len(centered) - lag] * centered[lag:]) / var_d
            if corr > best_corr:
                best_corr = corr
                best_lag = lag

    cycle_length[i] = float(best_lag)

    # Phase: find last local peak in detrended, compute position in cycle
    recent = detrended[-best_lag * 2:] if best_lag * 2 <= len(detrended) else detrended
    peaks = []
    for j in range(1, len(recent) - 1):
        if recent[j] > recent[j - 1] and recent[j] > recent[j + 1]:
            peaks.append(j)

    if len(peaks) > 0:
        bars_since_peak = len(recent) - 1 - peaks[-1]
        phase[i] = (bars_since_peak / best_lag) * 360.0
        phase[i] = phase[i] % 360.0
    else:
        phase[i] = 0.0

plot(cycle_length.tolist(), title="Cycle Length", color="#26A69A")
plot(phase.tolist(), title="Phase (0-360)", color="#AB47BC")
hline(0, title="Zero", color="#555555")
