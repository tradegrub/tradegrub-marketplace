from tg_scripting import *
import numpy as np

indicator("Demand Index", overlay=False)

length = input.int(14, "Length", minval=2, maxval=100)
smooth_len = input.int(5, "Smoothing", minval=1, maxval=20)
show_signal = input.bool(True, "Show Signal Line")

close_arr = np.array(close, dtype=float)
high_arr = np.array(high, dtype=float)
low_arr = np.array(low, dtype=float)
vol_arr = np.array(volume, dtype=float)
n = len(close_arr)

avg_vol = ta.sma(volume, length)
avg_vol_arr = np.array(avg_vol, dtype=float)
rel_vol = np.where(avg_vol_arr > 0, vol_arr / avg_vol_arr, 1.0)

price_range = high_arr - low_arr
mid_price = (high_arr + low_arr) / 2.0
price_change = np.zeros(n)
price_change[1:] = close_arr[1:] - close_arr[:-1]

buying_pressure = np.where(price_change > 0, rel_vol * price_change, 0.0)
selling_pressure = np.where(price_change < 0, rel_vol * np.abs(price_change), 0.0)

bp_sum = ta.sma(buying_pressure.tolist(), length)
sp_sum = ta.sma(selling_pressure.tolist(), length)
bp_arr = np.array(bp_sum, dtype=float)
sp_arr = np.array(sp_sum, dtype=float)

denom = bp_arr + sp_arr
di = np.where(denom != 0, ((bp_arr - sp_arr) / denom) * 100.0, 0.0)

di_signal = ta.ema(di.tolist(), smooth_len)


plot(di.tolist(), title="Demand Index", color="#42A5F5", linewidth=2)
if show_signal:
    plot(di_signal, title="Signal", color="#FFA726", linewidth=1)
hline(0.0, title="Zero", color="#555555", linestyle="dashed")
