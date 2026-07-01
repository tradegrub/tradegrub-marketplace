from tg_scripting import *
import numpy as np

indicator("Garman-Klass Volatility", overlay=False)

length = input.int(20, "Length", minval=5, maxval=100)
annualize = input.int(252, "Annualization Factor", minval=1, maxval=365)
smooth_len = input.int(5, "Smoothing", minval=1, maxval=20)
show_cc = input.bool(True, "Show Close-to-Close Volatility")

close_arr = np.array(close, dtype=float)
open_arr = np.array(open, dtype=float)
high_arr = np.array(high, dtype=float)
low_arr = np.array(low, dtype=float)
n = len(close_arr)

safe_open = np.where(open_arr > 0, open_arr, 1.0)
safe_low = np.where(low_arr > 0, low_arr, 1.0)

log_hl = np.log(high_arr / safe_low)
log_co = np.log(close_arr / safe_open)

gk_var = 0.5 * log_hl ** 2 - (2.0 * np.log(2.0) - 1.0) * log_co ** 2

gk_vol = np.zeros(n)
for i in range(length, n):
    window = gk_var[i - length + 1:i + 1]
    gk_vol[i] = np.sqrt(np.mean(window) * annualize) * 100.0

gk_smooth = ta.sma(gk_vol.tolist(), smooth_len)

# Close-to-close for comparison
log_ret = np.zeros(n)
log_ret[1:] = np.log(close_arr[1:] / np.where(close_arr[:-1] > 0, close_arr[:-1], 1.0))
cc_vol = np.zeros(n)
for i in range(length, n):
    window = log_ret[i - length + 1:i + 1]
    cc_vol[i] = np.std(window) * np.sqrt(annualize) * 100.0

plot(gk_vol.tolist(), title="GK Volatility", color="#42A5F5", linewidth=1)
plot(gk_smooth, title="GK Smooth", color="#FFA726", linewidth=2)
if show_cc:
    plot(cc_vol.tolist(), title="Close-to-Close Vol", color="#888888", linewidth=1)
