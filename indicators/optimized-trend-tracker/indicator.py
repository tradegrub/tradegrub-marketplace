from tg_scripting import *
import numpy as np

indicator("Optimized Trend Tracker", overlay=True)

length = input.int(20, "Length", minval=5, maxval=100)
percent = input.float(2.0, "Percent", minval=0.1, maxval=10.0)

cl = np.array(close, dtype=float)
n = len(cl)

# Compute EMA
alpha = 2.0 / (length + 1)
ema = np.zeros(n)
ema[0] = cl[0]
for i in range(1, n):
    ema[i] = alpha * cl[i] + (1 - alpha) * ema[i-1]

upper = ema * (1 + percent / 100)
lower = ema * (1 - percent / 100)

# OTT logic
ott = np.zeros(n)
ott[0] = cl[0]
for i in range(1, n):
    if cl[i] > upper[i]:
        ott[i] = upper[i]
    elif cl[i] < lower[i]:
        ott[i] = lower[i]
    else:
        ott[i] = ott[i-1]

# Direction
direction = np.where(cl > ott, 1, -1)
bull = (direction == 1)
bear = (direction == -1)

# Color by direction - plot two series
ott_bull = np.where(bull, ott, np.nan).tolist()
ott_bear = np.where(bear, ott, np.nan).tolist()

plot(ott_bull, title="OTT Bull", color="#4CAF50")
plot(ott_bear, title="OTT Bear", color="#f44336")
