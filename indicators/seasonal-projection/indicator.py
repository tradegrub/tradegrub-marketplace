from tg_scripting import *
import numpy as np

cycle_length = input.int(252, "Cycle Length", minval=20, maxval=1000)
num_cycles = input.int(5, "Number of Cycles", minval=2, maxval=20)

n = len(close)
close_arr = np.array([float(close[i]) for i in range(n)])

# Compute returns
returns = np.zeros(n)
returns[1:] = (close_arr[1:] - close_arr[:-1]) / (close_arr[:-1] + 0.0001)

# Compute seasonal score: average return at same relative position across past cycles
seasonal_score = np.zeros(n)
seasonal_strength = np.zeros(n)

min_history = cycle_length * 2

for i in range(min_history, n):
    pos = i % cycle_length
    cycle_returns = []
    for c in range(1, num_cycles + 1):
        idx = i - c * cycle_length
        if idx >= 0 and idx < n:
            cycle_returns.append(float(returns[idx]))

    if len(cycle_returns) >= 2:
        avg_ret = np.mean(cycle_returns)
        std_ret = np.std(cycle_returns)
        seasonal_score[i] = avg_ret * 1000.0  # Scale for visibility
        if std_ret > 0:
            seasonal_strength[i] = abs(avg_ret) / std_ret  # Consistency ratio
        else:
            seasonal_strength[i] = 0.0

# Smooth the seasonal score
kernel_size = min(5, n)
if kernel_size > 1:
    kernel = np.ones(kernel_size) / kernel_size
    smoothed = np.convolve(seasonal_score, kernel, mode='same')
else:
    smoothed = seasonal_score

plot(smoothed, title="Seasonal Score", color="#2196F3")
plot(seasonal_strength, title="Consistency", color="#FF9800")
hline(0, title="Zero", color="rgba(128,128,128,0.4)")

bullish_season = smoothed > 0.5
bearish_season = smoothed < -0.5
bgcolor(bullish_season, color="rgba(76,175,80,0.05)")
bgcolor(bearish_season, color="rgba(244,67,54,0.05)")
