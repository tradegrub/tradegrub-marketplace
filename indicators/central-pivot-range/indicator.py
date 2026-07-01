from tg_scripting import *
import numpy as np

indicator("Central Pivot Range", overlay=True)

period = input.int(20, "Lookback Period", minval=5, maxval=100)
narrow_threshold = input.int(50, "Narrow CPR Threshold %", minval=10, maxval=200)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

prev_high = np.array(ta.highest(high, period), dtype=float)
prev_low = np.array(ta.lowest(low, period), dtype=float)

prev_close = np.zeros(n)
for i in range(period, n):
    prev_close[i] = cl[i - period]
for i in range(period):
    prev_close[i] = cl[i]

pivot = (prev_high + prev_low + prev_close) / 3.0
bc = (prev_high + prev_low) / 2.0
tc = 2.0 * pivot - bc

cpr_width = np.abs(tc - bc)
width_pct = np.where(cl > 0, cpr_width / cl * 100.0, 0.0)

avg_width = np.zeros(n)
for i in range(period, n):
    avg_width[i] = np.mean(width_pct[i - period:i])
for i in range(period):
    avg_width[i] = width_pct[i]

threshold_mult = narrow_threshold / 100.0
narrow_cpr = np.zeros(n, dtype=bool)
for i in range(period, n):
    if avg_width[i] > 0 and width_pct[i] < avg_width[i] * threshold_mult:
        narrow_cpr[i] = True

p_pivot = plot(pivot.tolist(), title="Pivot", color="#ffab40", linewidth=2)
p_tc = plot(tc.tolist(), title="TC", color="#42a5f5", linewidth=1)
p_bc = plot(bc.tolist(), title="BC", color="#42a5f5", linewidth=1)

fill(p_tc, p_bc, color="rgba(66,165,245,0.12)")
bgcolor(narrow_cpr.tolist(), color="rgba(255,171,64,0.10)")
