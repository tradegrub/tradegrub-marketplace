from tg_scripting import *
import numpy as np

indicator("Fractal Adaptive Moving Average", overlay=True)

length = input.int(16, "Length", minval=4, maxval=100)

src = np.array(close)
h = np.array(high)
l = np.array(low)
n = len(src)
half = length // 2

frama = np.full(n, np.nan)

# Initialize
start = length
if start < n:
    frama[start] = src[start]

for i in range(start + 1, n):
    # Highest/lowest for first half, second half, full
    h1 = np.max(h[i - length:i - half])
    l1 = np.min(l[i - length:i - half])
    h2 = np.max(h[i - half:i])
    l2 = np.min(l[i - half:i])
    h3 = np.max(h[i - length:i])
    l3 = np.min(l[i - length:i])

    n1 = (h1 - l1) / half if (h1 - l1) > 0 else 0
    n2 = (h2 - l2) / half if (h2 - l2) > 0 else 0
    n3 = (h3 - l3) / length if (h3 - l3) > 0 else 0

    if n1 > 0 and n2 > 0 and n3 > 0:
        d = (np.log(n1 + n2) - np.log(n3)) / np.log(2)
    else:
        d = 1.0

    alpha = np.exp(-4.6 * (d - 1.0))
    alpha = max(0.01, min(1.0, alpha))

    frama[i] = alpha * src[i] + (1.0 - alpha) * frama[i - 1]

# Trend
rising = np.zeros(n, dtype=bool)
falling = np.zeros(n, dtype=bool)
for i in range(1, n):
    if not np.isnan(frama[i]) and not np.isnan(frama[i - 1]):
        if frama[i] > frama[i - 1]:
            rising[i] = True
        else:
            falling[i] = True

plot(frama.tolist(), title="FRAMA", color="#AB47BC", linewidth=2)
