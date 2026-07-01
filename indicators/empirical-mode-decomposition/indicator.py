from tg_scripting import *
import numpy as np

indicator("Empirical Mode Decomposition", overlay=False)

num_imfs = input.int(3, "Number of IMFs", minval=1, maxval=5)
max_iter = input.int(10, "Sifting Iterations", minval=3, maxval=30)

try:
    from scipy.interpolate import CubicSpline
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

src = np.array(close, dtype=float)
n = len(src)


def find_extrema(signal):
    maxima = []
    minima = []
    for i in range(1, len(signal) - 1):
        if signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
            maxima.append(i)
        elif signal[i] < signal[i - 1] and signal[i] < signal[i + 1]:
            minima.append(i)
    return maxima, minima


def envelope(indices, values, n):
    if len(indices) < 2:
        return np.full(n, np.mean(values)) if len(values) > 0 else np.zeros(n)
    if HAS_SCIPY:
        cs = CubicSpline(indices, values, bc_type='natural')
        return cs(np.arange(n))
    else:
        return np.interp(np.arange(n), indices, values)


def extract_imf(signal, iterations):
    h = signal.copy()
    for _ in range(iterations):
        maxima_idx, minima_idx = find_extrema(h)
        if len(maxima_idx) < 2 or len(minima_idx) < 2:
            break
        upper = envelope(maxima_idx, h[maxima_idx], len(h))
        lower = envelope(minima_idx, h[minima_idx], len(h))
        mean_env = (upper + lower) / 2.0
        h = h - mean_env
    return h


# Extract IMFs
residual = src - np.mean(src)
imfs = []
for i in range(num_imfs):
    imf = extract_imf(residual, max_iter)
    imfs.append(imf)
    residual = residual - imf

# Normalize IMFs for display
colors = ["#42A5F5", "#AB47BC", "#FFA726", "#4CAF50", "#EF5350"]
for i, imf in enumerate(imfs):
    std = np.std(imf)
    if std > 0:
        normalized = (imf / std) * 20
    else:
        normalized = imf
    offset = (i - num_imfs // 2) * 40
    plot((normalized + offset).tolist(), title=f"IMF {i + 1}", color=colors[i % len(colors)], linewidth=1)

hline(0, title="Zero", color="#555", linestyle="dashed")
