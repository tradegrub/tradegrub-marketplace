from tg_scripting import *
import numpy as np

indicator("Yang-Zhang Volatility", overlay=False)

length = input.int(20, "Length", minval=5, maxval=100)
annualize = input.int(252, "Annualization Factor", minval=1, maxval=365)
smooth_len = input.int(5, "Smoothing", minval=1, maxval=20)
show_components = input.bool(False, "Show Component Volatilities")

close_arr = np.array(close, dtype=float)
open_arr = np.array(open, dtype=float)
high_arr = np.array(high, dtype=float)
low_arr = np.array(low, dtype=float)
n = len(close_arr)

safe_prev_close = np.ones(n)
safe_prev_close[1:] = np.where(close_arr[:-1] > 0, close_arr[:-1], 1.0)
safe_open = np.where(open_arr > 0, open_arr, 1.0)
safe_low = np.where(low_arr > 0, low_arr, 1.0)

log_oc = np.zeros(n)
log_oc[1:] = np.log(open_arr[1:] / safe_prev_close[1:])

log_co = np.log(close_arr / safe_open)
log_ho = np.log(high_arr / safe_open)
log_lo = np.log(low_arr / safe_open)

rs_var = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)

yz_vol = np.zeros(n)
overnight_vol = np.zeros(n)
close_vol = np.zeros(n)
rs_vol_arr = np.zeros(n)

k = 0.34 / (1.34 + (length + 1.0) / (length - 1.0))

for i in range(length, n):
    ov = np.var(log_oc[i - length + 1:i + 1])
    cv = np.var(log_co[i - length + 1:i + 1])
    rv = np.mean(rs_var[i - length + 1:i + 1])

    total_var = ov + k * cv + (1.0 - k) * rv
    total_var = max(total_var, 0.0)
    yz_vol[i] = np.sqrt(total_var * annualize) * 100.0
    overnight_vol[i] = np.sqrt(max(ov, 0) * annualize) * 100.0
    close_vol[i] = np.sqrt(max(cv, 0) * annualize) * 100.0
    rs_vol_arr[i] = np.sqrt(max(rv, 0) * annualize) * 100.0

yz_smooth = ta.sma(yz_vol.tolist(), smooth_len)

plot(yz_vol.tolist(), title="YZ Volatility", color="#42A5F5", linewidth=1)
plot(yz_smooth, title="YZ Smooth", color="#FFA726", linewidth=2)
if show_components:
    plot(overnight_vol.tolist(), title="Overnight Vol", color="#ff1744", linewidth=1)
    plot(close_vol.tolist(), title="Close Vol", color="#00e676", linewidth=1)
    plot(rs_vol_arr.tolist(), title="RS Vol", color="#AB47BC", linewidth=1)
