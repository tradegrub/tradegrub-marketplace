from tg_scripting import *
import numpy as np

indicator("Day of Week Seasonality", overlay=False)

cycle_len = input.int(5, "Cycle Length", minval=3, maxval=10)
lookback = input.int(100, "Lookback Bars", minval=20, maxval=500)
show_wr = input.bool(True, "Show Win Rate")

src_c = np.array(close, dtype=float)
n = len(src_c)

returns = np.zeros(n)
for i in range(1, n):
    returns[i] = (src_c[i] - src_c[i - 1]) / (src_c[i - 1] + 1e-10) * 100.0

avg_return = np.full(n, np.nan)
win_rate_arr = np.full(n, np.nan)
bias = np.full(n, 0.0)

for i in range(lookback, n):
    day = i % cycle_len
    same_day = []
    for j in range(i - lookback, i):
        if j > 0 and j % cycle_len == day:
            same_day.append(returns[j])

    if len(same_day) >= 3:
        arr = np.array(same_day)
        avg_return[i] = np.mean(arr)
        wr = np.sum(arr > 0) / len(arr) * 100.0
        win_rate_arr[i] = wr

        if np.mean(arr) > 0.02:
            bias[i] = 1.0
        elif np.mean(arr) < -0.02:
            bias[i] = -1.0

bull_bias = bias > 0.5
bear_bias = bias < -0.5

plot(avg_return, title="Day Avg Return %", color="#42A5F5", linewidth=2)
if show_wr:
    plot(win_rate_arr, title="Win Rate %", color="#FFA726", linewidth=1)

hline(0, title="Zero", color="#555", linestyle="dashed")
hline(50, title="50% WR", color="rgba(255,167,38,0.3)", linestyle="dashed")

bgcolor(bull_bias, color="rgba(76,175,80,0.08)")
bgcolor(bear_bias, color="rgba(239,83,80,0.08)")
