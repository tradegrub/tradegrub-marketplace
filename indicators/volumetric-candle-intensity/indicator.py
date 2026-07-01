from tg_scripting import *
import numpy as np

indicator("Volumetric Candle Intensity", overlay=False)

vol_len = input.int(20, "Volume Lookback", minval=5, maxval=100)
std_mult = input.float(1.0, "StdDev Multiplier", minval=0.5, maxval=3.0, step=0.25)

vol = np.array(volume, dtype=np.float64)
cl = np.array(close, dtype=np.float64)
op = np.array(open, dtype=np.float64)
n = len(cl)

intensity = np.zeros(n)
vol_mean = np.zeros(n)
vol_std = np.zeros(n)

for i in range(vol_len, n):
    window = vol[i - vol_len:i]
    m = np.mean(window)
    s = np.std(window)
    vol_mean[i] = m
    vol_std[i] = s

    if s > 0:
        intensity[i] = (vol[i] - m) / (s * std_mult)
    else:
        intensity[i] = 0.0

capped = np.clip(intensity, -3.0, 3.0)

colors = []
for i in range(n):
    is_bull = cl[i] >= op[i]
    v = capped[i]

    if is_bull:
        if v > 2.0:
            colors.append("#00c853")
        elif v > 1.0:
            colors.append("#26a69a")
        elif v > 0:
            colors.append("rgba(38,166,154,0.6)")
        else:
            colors.append("rgba(38,166,154,0.3)")
    else:
        if v > 2.0:
            colors.append("#d50000")
        elif v > 1.0:
            colors.append("#ef5350")
        elif v > 0:
            colors.append("rgba(239,83,80,0.6)")
        else:
            colors.append("rgba(239,83,80,0.3)")

plot(capped.tolist(), title="Volume Intensity", color=colors, linewidth=2, style="histogram")
hline(0, title="Average", color="rgba(158,158,158,0.4)")
hline(1.0, title="+1 StdDev", color="rgba(255,235,59,0.3)", linestyle="dashed")
hline(2.0, title="+2 StdDev", color="rgba(255,152,0,0.3)", linestyle="dashed")
hline(-1.0, title="-1 StdDev", color="rgba(255,235,59,0.3)", linestyle="dashed")
