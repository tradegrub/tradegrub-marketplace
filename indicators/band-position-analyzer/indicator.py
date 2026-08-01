from tg_scripting import *
import numpy as np

indicator("Band Position Analyzer", overlay=False)

bb_len = input.int(20, "Bollinger Length", minval=10, maxval=50)
bb_mult = input.float(2.0, "Bollinger Mult", minval=1.0, maxval=4.0, step=0.5)
kc_len = input.int(20, "Keltner Length", minval=10, maxval=50)
dc_len = input.int(20, "Donchian Length", minval=10, maxval=50)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

bb_up, bb_mid, bb_lo = ta.bb(close, bb_len, bb_mult)
bb_up = np.array(bb_up, dtype=float)
bb_lo = np.array(bb_lo, dtype=float)
bb_range = bb_up - bb_lo
bb_pos = np.where(bb_range > 0, (cl - bb_lo) / bb_range * 100, 50.0)

ema_arr = np.array(ta.ema(close, kc_len), dtype=float)
atr_arr = np.array(ta.atr(high, low, close, kc_len), dtype=float)
ema_arr = np.nan_to_num(ema_arr, nan=0.0)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)
kc_up = ema_arr + 1.5 * atr_arr
kc_lo = ema_arr - 1.5 * atr_arr
kc_range = kc_up - kc_lo
kc_pos = np.where(kc_range > 0, (cl - kc_lo) / kc_range * 100, 50.0)

dc_hi = np.zeros(n)
dc_lo = np.zeros(n)
for i in range(dc_len, n):
    dc_hi[i] = np.max(hi[i-dc_len:i+1])
    dc_lo[i] = np.min(lo[i-dc_len:i+1])
dc_range = dc_hi - dc_lo
dc_pos = np.where(dc_range > 0, (cl - dc_lo) / dc_range * 100, 50.0)

avg_pos = (bb_pos + kc_pos + dc_pos) / 3.0

plot(bb_pos.tolist(), title="Bollinger %", color="#42a5f5", linewidth=1)
plot(kc_pos.tolist(), title="Keltner %", color="#ff9800", linewidth=1)
plot(dc_pos.tolist(), title="Donchian %", color="#ab47bc", linewidth=1)
plot(avg_pos.tolist(), title="Average Position", color="#ffffff", linewidth=2)
hline(80, title="Upper Zone", color="#4CAF50", linestyle="dashed")
hline(20, title="Lower Zone", color="#f44336", linestyle="dashed")
hline(50, title="Mid", color="#888888", linestyle="dashed")
