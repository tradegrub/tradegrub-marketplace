from tg_scripting import *
import numpy as np

indicator("Random Walk Index", overlay=False)

length = input.int(14, "Period", minval=2, maxval=100)
threshold = input.float(1.0, "Trend Threshold", minval=0.5, maxval=3.0, step=0.1)

n = len(close)
atr = ta.atr(high, low, close, length)

rwi_high = np.full(n, 0.0)
rwi_low = np.full(n, 0.0)

for i in range(length, n):
    max_rwi_h = 0.0
    max_rwi_l = 0.0
    for j in range(1, length + 1):
        if i - j >= 0 and atr[i] > 0:
            denom = atr[i] * np.sqrt(j)
            rh = (high[i] - low[i - j]) / denom
            rl = (high[i - j] - low[i]) / denom
            if rh > max_rwi_h:
                max_rwi_h = rh
            if rl > max_rwi_l:
                max_rwi_l = rl
    rwi_high[i] = max_rwi_h
    rwi_low[i] = max_rwi_l

uptrend = rwi_high > threshold
downtrend = rwi_low > threshold

plot(rwi_high, title="RWI High", color="#4CAF50", linewidth=2)
plot(rwi_low, title="RWI Low", color="#ff5252", linewidth=2)
hline(threshold, title="Threshold", color="#FFFFFF", linestyle="dashed")
hline(1.0, title="Unity", color="#666666", linestyle="dashed")

bgcolor(uptrend, color="rgba(76,175,80,0.08)")
bgcolor(downtrend, color="rgba(255,82,82,0.08)")
