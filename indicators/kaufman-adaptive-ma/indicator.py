from tg_scripting import *
import numpy as np

indicator("Kaufman Adaptive Moving Average", overlay=True)

length = input.int(10, "Length", minval=2, maxval=100)
fast_len = input.int(2, "Fast Period", minval=1, maxval=20)
slow_len = input.int(30, "Slow Period", minval=10, maxval=100)

src = np.array(close)
n = len(src)

fast_sc = 2.0 / (fast_len + 1.0)
slow_sc = 2.0 / (slow_len + 1.0)

kama = np.full(n, np.nan)
kama[length] = src[length]

for i in range(length + 1, n):
    # Direction
    direction = abs(src[i] - src[i - length])
    # Volatility (sum of absolute changes)
    volatility = 0.0
    for j in range(1, length + 1):
        volatility += abs(src[i - j + 1] - src[i - j])
    if volatility == 0:
        er = 0.0
    else:
        er = direction / volatility
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    kama[i] = kama[i - 1] + sc * (src[i] - kama[i - 1])

# Trend coloring
trend_up = np.zeros(n, dtype=bool)
trend_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if not np.isnan(kama[i]) and not np.isnan(kama[i - 1]):
        if kama[i] > kama[i - 1]:
            trend_up[i] = True
        else:
            trend_down[i] = True

plot(kama.tolist(), title="KAMA", color="#42A5F5", linewidth=2)
bgcolor(trend_down, color="rgba(255,23,68,0.04)")
