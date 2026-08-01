from tg_scripting import *
import numpy as np

indicator("Max Drawdown Tracker", overlay=False)

length = input.int(50, "Rolling Window", minval=10, maxval=500)
show_current = input.bool(True, "Show Current Drawdown")

c = np.array(close, dtype=float)
n = len(c)

running_max = np.full(n, np.nan)
current_dd = np.full(n, 0.0)
max_dd = np.full(n, 0.0)
bars_in_dd = np.full(n, 0.0)

running_max[0] = c[0]
for i in range(1, n):
    running_max[i] = max(running_max[i - 1], c[i])
    current_dd[i] = ((c[i] - running_max[i]) / running_max[i]) * 100.0

for i in range(length - 1, n):
    window = current_dd[i - length + 1:i + 1]
    max_dd[i] = np.min(window)

for i in range(n):
    if current_dd[i] < -0.01:
        bars_in_dd[i] = bars_in_dd[i - 1] + 1 if i > 0 else 1
    else:
        bars_in_dd[i] = 0

deep_dd = np.array([current_dd[i] < -5.0 for i in range(n)])

plot(max_dd, title="Max Drawdown", color="#EF5350", linewidth=2)
if show_current:
    plot(current_dd, title="Current DD", color="#FF9800", linewidth=1)
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
hline(-5.0, title="-5%", color="#FFEB3B", linestyle="dashed")
hline(-10.0, title="-10%", color="#EF5350", linestyle="dashed")
bgcolor(deep_dd, color="rgba(244,67,54,0.08)")
