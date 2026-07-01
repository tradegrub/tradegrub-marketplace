from tg_scripting import *
import numpy as np

indicator("Variable Index Dynamic Average", overlay=True)

length = input.int(14, "Length", minval=2, maxval=100)
cmo_len = input.int(9, "CMO Length", minval=2, maxval=50)

src = np.array(close)
n = len(src)

# Chande Momentum Oscillator ratio
sc = 2.0 / (length + 1.0)

vidya = np.full(n, np.nan)
vidya[cmo_len] = src[cmo_len]

for i in range(cmo_len + 1, n):
    # CMO calculation
    up_sum = 0.0
    down_sum = 0.0
    for j in range(1, cmo_len + 1):
        diff = src[i - j + 1] - src[i - j]
        if diff > 0:
            up_sum += diff
        else:
            down_sum += abs(diff)
    total = up_sum + down_sum
    cmo_ratio = abs(up_sum - down_sum) / total if total != 0 else 0.0

    prev = vidya[i - 1]
    if np.isnan(prev):
        vidya[i] = src[i]
    else:
        vidya[i] = prev + sc * cmo_ratio * (src[i] - prev)

# EMA reference
ema_ref = ta.ema(close, length)

# Trend
rising = np.zeros(n, dtype=bool)
falling = np.zeros(n, dtype=bool)
for i in range(1, n):
    if not np.isnan(vidya[i]) and not np.isnan(vidya[i - 1]):
        if vidya[i] > vidya[i - 1]:
            rising[i] = True
        else:
            falling[i] = True

plot(vidya.tolist(), title="VIDYA", color="#26C6DA", linewidth=2)
plot(ema_ref, title="EMA Reference", color="rgba(255,255,255,0.2)", linewidth=1)
