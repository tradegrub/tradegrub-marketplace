from tg_scripting import *
import numpy as np

indicator("Polarized Fractal Efficiency", overlay=False)

length = input.int(10, "Length", minval=2, maxval=100)
smooth = input.int(5, "Smoothing", minval=1, maxval=20)

src = np.array(close)
n = len(src)

pfe_raw = np.full(n, 0.0)

for i in range(length, n):
    # Net distance (straight line)
    net = src[i] - src[i - length]
    # Path length (sum of bar-to-bar distances)
    path = 0.0
    for j in range(1, length + 1):
        diff = src[i - j + 1] - src[i - j]
        path += np.sqrt(1.0 + diff * diff)

    straight = np.sqrt(float(length * length) + net * net)
    if path == 0:
        pfe_raw[i] = 0.0
    else:
        eff = straight / path * 100.0
        pfe_raw[i] = eff if net > 0 else -eff

# Smooth with EMA
pfe = np.array(ta.ema(pfe_raw.tolist(), smooth))

# Zones
strong_up = pfe > 50
strong_down = pfe < -50

plot(pfe.tolist(), title="PFE", color="#42A5F5", linewidth=2)
hline(50.0, title="Strong Up", color="rgba(0,230,118,0.4)", linestyle="dashed")
hline(0.0, title="Zero", color="#555555", linestyle="dashed")
hline(-50.0, title="Strong Down", color="rgba(255,23,68,0.4)", linestyle="dashed")
bgcolor(strong_up, color="rgba(0,230,118,0.06)")
bgcolor(strong_down, color="rgba(255,23,68,0.06)")
