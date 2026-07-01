from tg_scripting import *
import numpy as np

indicator("Momentum Candle Mapper", overlay=False)

mom_len = input.int(10, "Momentum Length", minval=3, maxval=30)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)
use_ha = input.bool(True, "Use Smoothed Mode")

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
op = np.array(open, dtype=float)
n = len(cl)

mom_cl = np.zeros(n)
mom_hi = np.zeros(n)
mom_lo = np.zeros(n)
mom_op = np.zeros(n)
for i in range(mom_len, n):
    mom_cl[i] = (cl[i] - cl[i-mom_len]) / max(cl[i-mom_len], 1e-10) * 100
    mom_hi[i] = (hi[i] - hi[i-mom_len]) / max(hi[i-mom_len], 1e-10) * 100
    mom_lo[i] = (lo[i] - lo[i-mom_len]) / max(lo[i-mom_len], 1e-10) * 100
    mom_op[i] = (op[i] - op[i-mom_len]) / max(op[i-mom_len], 1e-10) * 100

if use_ha:
    ha_cl = (mom_op + mom_hi + mom_lo + mom_cl) / 4
    ha_op = np.copy(mom_op)
    for i in range(1, n):
        ha_op[i] = (ha_op[i-1] + ha_cl[i-1]) / 2
    ha_hi = np.maximum(np.maximum(mom_hi, ha_op), ha_cl)
    ha_lo = np.minimum(np.minimum(mom_lo, ha_op), ha_cl)
    mom_cl = ha_cl
    mom_op = ha_op
    mom_hi = ha_hi
    mom_lo = ha_lo

if smooth > 1:
    mom_cl = np.array(ta.sma(mom_cl.tolist(), smooth), dtype=float)
    mom_cl = np.nan_to_num(mom_cl, nan=0.0)


plot(mom_cl.tolist(), title="Momentum Close", color="#42a5f5", linewidth=2)
plot(mom_op.tolist(), title="Momentum Open", color="#78909C", linewidth=1)
hline(0, title="Zero", color="#888888", linestyle="dashed")
