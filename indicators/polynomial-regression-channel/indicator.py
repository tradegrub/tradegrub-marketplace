from tg_scripting import *
import numpy as np

indicator("Polynomial Regression Channel", overlay=True)

length = input.int(50, "Lookback Length", minval=20, maxval=200)
degree = input.int(3, "Polynomial Degree", minval=1, maxval=5)
mult = input.float(2.0, "Channel Width (StdDev)", minval=0.5, maxval=4.0, step=0.5)

src = np.array(close, dtype=float)
n = len(src)

center = np.full(n, np.nan)
upper = np.full(n, np.nan)
lower = np.full(n, np.nan)

for i in range(length, n):
    window = src[i - length + 1:i + 1]
    x = np.arange(length, dtype=float)

    coeffs = np.polyfit(x, window, degree)
    fitted = np.polyval(coeffs, x)

    residuals = window - fitted
    std = np.std(residuals)

    center[i] = fitted[-1]
    upper[i] = fitted[-1] + std * mult
    lower[i] = fitted[-1] - std * mult

# Price above/below channel
above = np.zeros(n, dtype=bool)
below = np.zeros(n, dtype=bool)
for i in range(length, n):
    if not np.isnan(upper[i]):
        above[i] = src[i] > upper[i]
    if not np.isnan(lower[i]):
        below[i] = src[i] < lower[i]

plot(center.tolist(), title="Poly Center", color="#42a5f5", linewidth=2)
plot(upper.tolist(), title="Upper Band", color="#ef5350", linewidth=1)
plot(lower.tolist(), title="Lower Band", color="#26a69a", linewidth=1)

bgcolor(above.tolist(), color="rgba(239,83,80,0.08)")
bgcolor(below.tolist(), color="rgba(38,166,154,0.08)")

plotshape(above.tolist(), title="Above Channel", style="triangledown",
          location="abovebar", color="#ef5350")
plotshape(below.tolist(), title="Below Channel", style="triangleup",
          location="belowbar", color="#26a69a")
