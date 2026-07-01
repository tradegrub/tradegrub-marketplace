from tg_scripting import *
import numpy as np

indicator("Jurik Moving Average", overlay=True)

length = input.int(7, "Length", minval=1, maxval=100)
phase = input.int(50, "Phase", minval=-100, maxval=100)
power = input.float(2.0, "Power", minval=0.5, maxval=5.0, step=0.1)

src = np.array(close)
n = len(src)

# Phase ratio
if phase < -100:
    phase_ratio = 0.5
elif phase > 100:
    phase_ratio = 2.5
else:
    phase_ratio = phase / 100.0 + 1.5

beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2.0)
alpha = beta ** power

jma = np.full(n, np.nan)
e0 = np.zeros(n)
e1 = np.zeros(n)
e2 = np.zeros(n)

e0[0] = src[0]
e1[0] = 0.0
e2[0] = 0.0
jma[0] = src[0]

for i in range(1, n):
    e0[i] = (1.0 - alpha) * src[i] + alpha * e0[i - 1]
    e1[i] = (src[i] - e0[i]) * (1.0 - beta) + beta * e1[i - 1]
    e2[i] = (e0[i] + phase_ratio * e1[i] - jma[i - 1]) * (1.0 - alpha) ** 2 + alpha ** 2 * e2[i - 1]
    jma[i] = jma[i - 1] + e2[i]

# Standard EMA for comparison
ema_ref = ta.ema(close, length)

# Trend
rising = np.zeros(n, dtype=bool)
falling = np.zeros(n, dtype=bool)
for i in range(1, n):
    if not np.isnan(jma[i]) and not np.isnan(jma[i - 1]):
        if jma[i] > jma[i - 1]:
            rising[i] = True
        else:
            falling[i] = True

plot(jma.tolist(), title="JMA", color="#FFD54F", linewidth=2)
plot(ema_ref, title="EMA Reference", color="rgba(255,255,255,0.2)", linewidth=1)
