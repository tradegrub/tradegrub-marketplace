from tg_scripting import *
import numpy as np

indicator("Hurst Exponent", overlay=False)

length = input.int(100, "Lookback Length", minval=50, maxval=500)
max_lag = input.int(20, "Max Lag", minval=5, maxval=50)

c = np.array(close, dtype=float)
n = len(c)

hurst = np.full(n, np.nan)

for i in range(length - 1, n):
    series = c[i - length + 1:i + 1]
    lags = range(2, min(max_lag + 1, length // 4))
    tau = []
    lag_list = []
    for lag in lags:
        diffs = series[lag:] - series[:-lag]
        std_val = np.std(diffs)
        if std_val > 1e-10:
            tau.append(std_val)
            lag_list.append(lag)
    if len(lag_list) >= 3:
        log_lags = np.log(np.array(lag_list, dtype=float))
        log_tau = np.log(np.array(tau, dtype=float))
        coeffs = np.polyfit(log_lags, log_tau, 1)
        hurst[i] = max(0.0, min(1.0, coeffs[0]))

hurst_sma = np.full(n, np.nan)
sm = 10
for i in range(length + sm - 2, n):
    vals = hurst[i - sm + 1:i + 1]
    valid = vals[~np.isnan(vals)]
    if len(valid) > 0:
        hurst_sma[i] = np.mean(valid)

trending = np.array([not np.isnan(hurst[i]) and hurst[i] > 0.6 for i in range(n)])
mean_rev = np.array([not np.isnan(hurst[i]) and hurst[i] < 0.4 for i in range(n)])

plot(hurst, title="Hurst Exponent", color="#42A5F5", linewidth=2)
plot(hurst_sma, title="Smoothed", color="#FF9800", linewidth=1)
hline(0.5, title="Random Walk", color="#FFFFFF", linestyle="dashed")
hline(0.6, title="Trending", color="#66BB6A", linestyle="dashed")
hline(0.4, title="Mean Reverting", color="#EF5350", linestyle="dashed")
bgcolor(trending, color="rgba(76,175,80,0.08)")
bgcolor(mean_rev, color="rgba(244,67,54,0.08)")
