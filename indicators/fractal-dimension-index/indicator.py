from tg_scripting import *
import numpy as np

indicator("Fractal Dimension Index", overlay=False)

length = input.int(30, "Length", minval=10, maxval=100)

src = np.array(close, dtype=float)
n = len(src)

fdi = np.full(n, 1.5)

for i in range(length, n):
    window = src[i - length + 1:i + 1]
    wlen = len(window)

    # Rescaled Range (R/S) analysis for Hurst exponent
    mean_val = np.mean(window)
    deviations = window - mean_val
    cumulative = np.cumsum(deviations)
    R = float(np.max(cumulative) - np.min(cumulative))
    S = float(np.std(window, ddof=1))

    if S > 0 and R > 0:
        rs = R / S
        # Hurst exponent: H = log(R/S) / log(n)
        H = np.log(rs) / np.log(float(wlen))
        H = min(1.0, max(0.0, float(H)))
    else:
        H = 0.5

    # Fractal dimension D = 2 - H
    fdi[i] = 2.0 - H

# Smooth
kern = np.ones(3) / 3
fdi_smooth = np.convolve(fdi, kern, mode='same')

plot(fdi_smooth.tolist(), title="Fractal Dimension", color="#42A5F5", linewidth=2)
hline(1.7, title="Mean-Reverting Zone", color="#EF5350", linestyle="dashed")
hline(1.5, title="Random Walk", color="#FFA726", linestyle="dashed")
hline(1.3, title="Trending Zone", color="#4CAF50", linestyle="dashed")
