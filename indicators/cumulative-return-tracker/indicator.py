from tg_scripting import *
import numpy as np

indicator("Cumulative Return Tracker", overlay=False)

bench_len = input.int(50, "Benchmark SMA Length", minval=10, maxval=200)

cl = np.array(close, dtype=float)
n = len(cl)

daily_ret = np.zeros(n)
for i in range(1, n):
    daily_ret[i] = (cl[i] - cl[i-1]) / max(cl[i-1], 1e-10)

cum_ret = np.zeros(n)
cum_ret[0] = 100
for i in range(1, n):
    cum_ret[i] = cum_ret[i-1] * (1 + daily_ret[i])

peak = np.zeros(n)
drawdown = np.zeros(n)
peak[0] = cum_ret[0]
for i in range(1, n):
    peak[i] = max(peak[i-1], cum_ret[i])
    drawdown[i] = (cum_ret[i] - peak[i]) / max(peak[i], 1e-10) * 100

sma_arr = np.array(ta.sma(close, bench_len), dtype=float)
sma_arr = np.nan_to_num(sma_arr, nan=0.0)
bench_ret = np.zeros(n)
bench_ret[0] = 100
in_market = cl > sma_arr
for i in range(1, n):
    if in_market[i-1]:
        bench_ret[i] = bench_ret[i-1] * (1 + daily_ret[i])
    else:
        bench_ret[i] = bench_ret[i-1]

plot(cum_ret.tolist(), title="Cumulative Return", color="#42a5f5", linewidth=2)
plot(bench_ret.tolist(), title=f"SMA({bench_len}) Filtered", color="#ff9800", linewidth=1)
plot(drawdown.tolist(), title="Drawdown %", color="#ef5350", linewidth=1)
hline(100, title="Breakeven", color="#888888", linestyle="dashed")
hline(0, title="Zero DD", color="#888888", linestyle="dashed")

deep_dd = drawdown < -10
bgcolor(deep_dd.tolist(), color="rgba(244,67,54,0.06)")
