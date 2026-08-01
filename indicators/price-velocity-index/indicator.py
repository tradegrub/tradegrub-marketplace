from tg_scripting import *
import numpy as np

indicator("Price Velocity Index", overlay=False)

length = input.int(10, "Velocity Length", minval=3, maxval=30)
smooth = input.int(5, "Smoothing", minval=2, maxval=20)
accel_len = input.int(5, "Acceleration Length", minval=2, maxval=15)

src = np.array(close, dtype=float)
n = len(src)

smoothed = np.copy(src)
for _ in range(3):
    temp = np.copy(smoothed)
    for i in range(1, n):
        temp[i] = 0.7 * smoothed[i] + 0.3 * temp[i-1]
    smoothed = temp

velocity = np.zeros(n)
for i in range(length, n):
    velocity[i] = (smoothed[i] - smoothed[i - length]) / max(abs(smoothed[i - length]), 1e-10) * 100

vel_smooth = np.array(ta.sma(velocity.tolist(), smooth), dtype=float)
vel_smooth = np.nan_to_num(vel_smooth, nan=0.0)

accel = np.zeros(n)
for i in range(accel_len, n):
    accel[i] = vel_smooth[i] - vel_smooth[i - accel_len]

speeding_up = (vel_smooth > 0) & (accel > 0)
slowing_down = (vel_smooth > 0) & (accel < 0)

plot(vel_smooth.tolist(), title="Velocity", color="#29b6f6", linewidth=2)
plot(accel.tolist(), title="Acceleration", color="#ff7043", linewidth=1)
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(speeding_up.tolist(), color="rgba(76,175,80,0.06)")
bgcolor(slowing_down.tolist(), color="rgba(255,152,0,0.06)")
