from tg_scripting import *
import numpy as np

indicator("Period Return Analyzer", overlay=False)

period = input.int(20, "Return Period", minval=5, maxval=100)
hist_window = input.int(100, "History Window", minval=50, maxval=252)

cl = np.array(close, dtype=float)
n = len(cl)

returns = np.zeros(n)
for i in range(period, n):
    returns[i] = (cl[i] - cl[i-period]) / max(cl[i-period], 1e-10) * 100

avg_ret = np.zeros(n)
std_ret = np.zeros(n)
percentile = np.zeros(n)

start = max(period, hist_window)
for i in range(start, n):
    window = returns[i-hist_window:i+1]
    valid = window[window != 0]
    if len(valid) > 2:
        avg_ret[i] = np.mean(valid)
        std_ret[i] = np.std(valid)
        percentile[i] = np.sum(valid <= returns[i]) / len(valid) * 100

upper_band = avg_ret + std_ret
lower_band = avg_ret - std_ret

extreme_high = percentile > 90
extreme_low = percentile < 10

plot(returns.tolist(), title="Period Return %", color="#42a5f5", linewidth=2)
plot(avg_ret.tolist(), title="Mean Return", color="#888888", linewidth=1)
plot(upper_band.tolist(), title="+1 Std Dev", color="#4CAF50", linewidth=1)
plot(lower_band.tolist(), title="-1 Std Dev", color="#f44336", linewidth=1)
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(extreme_high.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(extreme_low.tolist(), color="rgba(244,67,54,0.08)")
