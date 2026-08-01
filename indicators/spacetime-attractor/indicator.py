from tg_scripting import *
import numpy as np

lookback = input.int(30, "Lookback", minval=5, maxval=200)
threshold = input.float(2.0, "Threshold", minval=0.1, maxval=10.0)

n = len(close)
close_arr = np.array([float(close[i]) for i in range(n)])
vol_arr = np.array([float(volume[i]) for i in range(n)])

# Rolling mean price
rolling_mean = np.zeros(n)
for i in range(n):
    start = max(0, i - lookback + 1)
    rolling_mean[i] = np.mean(close_arr[start:i + 1])

# "Mass" = rolling volume concentration (normalized rolling sum of volume)
rolling_vol = np.zeros(n)
for i in range(n):
    start = max(0, i - lookback + 1)
    rolling_vol[i] = np.sum(vol_arr[start:i + 1])

# Normalize mass to 0-1 range
vol_max = np.max(rolling_vol) if np.max(rolling_vol) > 0 else 1.0
mass = rolling_vol / vol_max

# "Curvature" = second derivative of price (acceleration)
velocity = np.zeros(n)
velocity[1:] = close_arr[1:] - close_arr[:-1]
acceleration = np.zeros(n)
acceleration[1:] = velocity[1:] - velocity[:-1]

# Normalize acceleration
acc_std = np.std(acceleration[lookback:]) if n > lookback else 1.0
if acc_std == 0:
    acc_std = 1.0
curvature = acceleration / acc_std

# Distance from mean
distance = close_arr - rolling_mean
dist_pct = distance / (rolling_mean + 0.0001) * 100.0

# Attractor force = mass * curvature / distance^2
# When price is far from mean and curvature points back, force is strong
distance_sq = dist_pct ** 2 + 0.01  # avoid division by zero
attractor_force = mass * curvature / distance_sq * 100.0

# Smooth the force
kernel_size = min(5, n)
kernel = np.ones(kernel_size) / kernel_size
force_smooth = np.convolve(attractor_force, kernel, mode='same')

# Mean reversion signal: force exceeds threshold while price is extended
reversion_signal = (np.abs(force_smooth) > threshold) & (np.abs(dist_pct) > 1.0)

plot(force_smooth, title="Attractor Force", color="#2196F3")
plot(dist_pct, title="Distance from Mean %", color="#FF9800")
hline(threshold, title="Upper Threshold", color="rgba(76,175,80,0.4)")
hline(-threshold, title="Lower Threshold", color="rgba(244,67,54,0.4)")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")

plotshape(reversion_signal & (dist_pct > 0), title="Pull Down", style="triangledown", location="top", color="#F44336")
plotshape(reversion_signal & (dist_pct < 0), title="Pull Up", style="triangleup", location="bottom", color="#4CAF50")
