from tg_scripting import *
import numpy as np

length = input.int(14, "Length", minval=2, maxval=100)

n = len(close)
high_arr = np.array([float(high[i]) for i in range(n)])
low_arr = np.array([float(low[i]) for i in range(n)])
vol_arr = np.array([float(volume[i]) for i in range(n)])

# Midpoint
mid = (high_arr + low_arr) / 2.0

# Distance moved
prev_mid = np.roll(mid, 1)
prev_mid[0] = mid[0]
distance = mid - prev_mid

# Box ratio
hl_range = high_arr - low_arr + 0.001
box_ratio = (vol_arr / 1000000.0) / hl_range

# Raw EMV
emv_raw = distance / (box_ratio + 0.0001)

# SMA smoothing using numpy convolution
kernel = np.ones(length) / length
emv = np.convolve(emv_raw, kernel, mode='same')

# Signal line (double smoothed)
signal = np.convolve(emv, kernel, mode='same')

plot(emv, title="EMV", color="#2196F3")
plot(signal, title="Signal", color="#FF9800")
hline(0, title="Zero", color="rgba(128,128,128,0.4)")

bullish = (emv > 0) & (emv > signal)
bearish = (emv < 0) & (emv < signal)
bgcolor(bullish, color="rgba(76,175,80,0.05)")
bgcolor(bearish, color="rgba(244,67,54,0.05)")
