from tg_scripting import *
import numpy as np

indicator("Profit Factor Tracker", overlay=False)

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
warn_level = input.float(1.0, "Warning Level", minval=0.5, maxval=2.0, step=0.1)
good_level = input.float(1.5, "Good Level", minval=1.0, maxval=3.0, step=0.1)

n = len(close)
profit_factor = np.ones(n)
gross_profit = np.zeros(n)
gross_loss = np.zeros(n)
cumulative_pf = np.ones(n)
total_gp = 0.0
total_gl = 0.0

for i in range(1, n):
    ret = close[i] - close[i - 1]
    if ret > 0:
        total_gp += ret
    elif ret < 0:
        total_gl += abs(ret)
    cumulative_pf[i] = total_gp / total_gl if total_gl > 0 else 2.0

    start = max(1, i - lookback + 1)
    gp = 0.0
    gl = 0.0
    for j in range(start, i + 1):
        r = close[j] - close[j - 1]
        if r > 0:
            gp += r
        elif r < 0:
            gl += abs(r)
    gross_profit[i] = gp
    gross_loss[i] = gl
    profit_factor[i] = gp / gl if gl > 0 else 2.0

profit_factor = np.clip(profit_factor, 0, 5.0)
cumulative_pf = np.clip(cumulative_pf, 0, 5.0)

above_good = np.array([profit_factor[i] >= good_level for i in range(n)], dtype=bool)
below_warn = np.array([profit_factor[i] < warn_level for i in range(n)], dtype=bool)

plot(profit_factor, title="Rolling PF", color="#42a5f5", linewidth=2)
plot(cumulative_pf, title="Cumulative PF", color="#ffa726", linewidth=1)
hline(warn_level, title="Warning", color="#ff5252", linestyle="dashed")
hline(good_level, title="Good", color="#00e676", linestyle="dashed")
hline(1.0, title="Breakeven", color="#555555", linestyle="dashed")
bgcolor(above_good, color="rgba(76,175,80,0.06)")
bgcolor(below_warn, color="rgba(255,82,82,0.06)")
