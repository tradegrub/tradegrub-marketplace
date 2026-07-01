from tg_scripting import *
import numpy as np
from scipy.stats import zscore as scipy_zscore

indicator("Normalized Return Extremes", overlay=False)

ret_len = input.int(5, "Return Period", minval=1, maxval=20)
norm_window = input.int(60, "Normalization Window", minval=30, maxval=200)
extreme_z = input.float(2.0, "Extreme Threshold (z)", minval=1.0, maxval=3.0, step=0.25)

cl = np.array(close, dtype=float)
n = len(cl)

returns = np.zeros(n)
for i in range(ret_len, n):
    returns[i] = (cl[i] - cl[i-ret_len]) / max(cl[i-ret_len], 1e-10) * 100

atr_arr = np.array(ta.atr(high, low, close, 14), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

norm_ret = np.zeros(n)
for i in range(norm_window, n):
    vol = np.mean(atr_arr[i-norm_window:i])
    if vol > 0:
        norm_ret[i] = returns[i] / (vol / max(cl[i], 1e-10) * 100)

z_score = np.zeros(n)
for i in range(norm_window, n):
    window = norm_ret[i-norm_window:i]
    mu = np.mean(window)
    std = np.std(window)
    if std > 0:
        z_score[i] = (norm_ret[i] - mu) / std

regime = np.zeros(n)
for i in range(norm_window * 2, n):
    recent = np.std(norm_ret[i-norm_window//2:i])
    historical = np.std(norm_ret[i-norm_window:i-norm_window//2])
    if historical > 0:
        regime[i] = recent / historical

extreme_up = z_score > extreme_z
extreme_down = z_score < -extreme_z

plot(z_score.tolist(), title="Normalized Z-Score", color="#e040fb", linewidth=2)
plot(regime.tolist(), title="Volatility Regime", color="#78909C", linewidth=1)
hline(extreme_z, title="Upper Extreme", color="#f44336", linestyle="dashed")
hline(-extreme_z, title="Lower Extreme", color="#4CAF50", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
hline(1, title="Regime Baseline", color="#ff9800", linestyle="dashed")
bgcolor(extreme_up.tolist(), color="rgba(244,67,54,0.08)")
bgcolor(extreme_down.tolist(), color="rgba(76,175,80,0.08)")
