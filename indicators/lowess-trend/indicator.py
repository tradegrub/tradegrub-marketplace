from tg_scripting import *
import numpy as np

bandwidth = input.int(20, "Bandwidth", minval=5, maxval=100)

src = np.array(close, dtype=float)
n = len(src)

# LOWESS: locally weighted scatterplot smoothing with tricube kernel
smoothed = np.full(n, np.nan)
x_all = np.arange(n, dtype=float)

for i in range(n):
    # Distance from point i to all other points
    dists = np.abs(x_all - float(i))

    # Use bandwidth as half-window
    half_w = bandwidth
    start = max(0, i - half_w)
    end = min(n, i + half_w + 1)

    x_local = x_all[start:end]
    y_local = src[start:end]
    d_local = dists[start:end]

    # Tricube weights
    max_d = float(np.max(d_local)) + 1e-10
    u = d_local / max_d
    weights = np.power(1.0 - np.power(u, 3), 3)
    weights = np.maximum(weights, 0.0)

    # Weighted least squares: fit y = a + b*x
    sw = float(np.sum(weights))
    if sw > 0:
        swx = float(np.sum(weights * x_local))
        swy = float(np.sum(weights * y_local))
        swxx = float(np.sum(weights * x_local * x_local))
        swxy = float(np.sum(weights * x_local * y_local))

        denom = sw * swxx - swx * swx
        if abs(denom) > 1e-10:
            b = (sw * swxy - swx * swy) / denom
            a = (swy - b * swx) / sw
            smoothed[i] = a + b * float(i)
        else:
            smoothed[i] = swy / sw
    else:
        smoothed[i] = src[i]

# Color based on price vs smoothed
above = src > smoothed
colors = np.where(above, color.green, color.red)

plot(smoothed.tolist(), title="LOWESS", color=colors.tolist())

# Breakout shapes
cross_above = np.zeros(n, dtype=bool)
cross_below = np.zeros(n, dtype=bool)
cross_above[1:] = (src[1:] > smoothed[1:]) & (src[:-1] <= smoothed[:-1])
cross_below[1:] = (src[1:] < smoothed[1:]) & (src[:-1] >= smoothed[:-1])

plotshape(cross_above, title="Cross Above", style="triangleup", location="belowbar", color=color.green)
plotshape(cross_below, title="Cross Below", style="triangledown", location="abovebar", color=color.red)
