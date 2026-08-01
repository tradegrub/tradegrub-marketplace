from tg_scripting import *
import numpy as np

indicator("Monthly Seasonality Index", overlay=False)

cycle_len = input.int(12, "Cycle Length", minval=4, maxval=52)
lookback = input.int(120, "Lookback Bars", minval=24, maxval=600)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)

src_c = np.array(close, dtype=float)
n = len(src_c)

returns = np.zeros(n)
for i in range(1, n):
    returns[i] = (src_c[i] - src_c[i - 1]) / (src_c[i - 1] + 1e-10) * 100.0

seasonal_idx = np.full(n, np.nan)
cumul_season = np.full(n, np.nan)
consistency = np.full(n, np.nan)

for i in range(lookback, n):
    month = i % cycle_len
    same_month = []
    for j in range(i - lookback, i):
        if j > 0 and j % cycle_len == month:
            same_month.append(returns[j])

    if len(same_month) >= 3:
        arr = np.array(same_month)
        mean_r = np.mean(arr)
        seasonal_idx[i] = mean_r

        pos_count = np.sum(arr > 0)
        neg_count = np.sum(arr <= 0)
        total = len(arr)
        consistency[i] = abs(pos_count - neg_count) / total * 100.0

if smooth > 1:
    smoothed = np.full(n, np.nan)
    for i in range(smooth, n):
        vals = seasonal_idx[i - smooth + 1:i + 1]
        valid = vals[~np.isnan(vals)]
        if len(valid) > 0:
            smoothed[i] = np.mean(valid)
    seasonal_idx = smoothed

cumsum = 0.0
for i in range(n):
    if not np.isnan(seasonal_idx[i]):
        cumsum += seasonal_idx[i]
    cumul_season[i] = cumsum

bull_season = np.array([not np.isnan(seasonal_idx[i]) and seasonal_idx[i] > 0.05 for i in range(n)])
bear_season = np.array([not np.isnan(seasonal_idx[i]) and seasonal_idx[i] < -0.05 for i in range(n)])

plot(seasonal_idx, title="Seasonal Index", color="#42A5F5", linewidth=2)
plot(consistency, title="Consistency %", color="#FFA726", linewidth=1)

hline(0, title="Zero", color="#555", linestyle="dashed")

bgcolor(bull_season, color="rgba(76,175,80,0.08)")
bgcolor(bear_season, color="rgba(239,83,80,0.08)")
