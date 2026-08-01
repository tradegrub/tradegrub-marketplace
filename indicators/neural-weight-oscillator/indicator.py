from tg_scripting import *
import numpy as np

lookback = input.int(20, "Lookback", minval=5, maxval=100)
weight_period = input.int(50, "Weight Period", minval=10, maxval=200)

src = close
n = len(src)

# Sub-score 1: Trend (EMA slope normalized)
ema_val = ta.ema(src, lookback)
slope = np.zeros(n)
slope[1:] = np.array(ema_val[1:]) - np.array(ema_val[:-1])
slope_std = np.zeros(n)
for i in range(lookback, n):
    s = slope[i - lookback:i]
    std_val = float(np.std(s))
    slope_std[i] = slope[i] / std_val if std_val > 0 else 0.0
trend_score = np.clip(slope_std, -1, 1)

# Sub-score 2: Momentum (RSI rescaled to -1..1)
rsi_val = np.array(ta.rsi(src, lookback), dtype=float)
momentum_score = (rsi_val - 50.0) / 50.0

# Sub-score 3: Mean-reversion (z-score from SMA)
sma_val = np.array(ta.sma(src, lookback), dtype=float)
src_arr = np.array(src, dtype=float)
zscore = np.zeros(n)
for i in range(lookback, n):
    window = src_arr[i - lookback:i]
    std_val = float(np.std(window))
    zscore[i] = (src_arr[i] - sma_val[i]) / std_val if std_val > 0 else 0.0
reversion_score = np.clip(-zscore, -1, 1)

# Next-bar returns
returns = np.zeros(n)
returns[:-1] = (src_arr[1:] - src_arr[:-1]) / np.where(src_arr[:-1] != 0, src_arr[:-1], 1.0)

# Rolling correlation for predictive accuracy weights
w_trend = np.zeros(n)
w_momentum = np.zeros(n)
w_reversion = np.zeros(n)

for i in range(weight_period, n):
    r = returns[i - weight_period:i]
    t = trend_score[i - weight_period:i]
    m = momentum_score[i - weight_period:i]
    v = reversion_score[i - weight_period:i]

    r_std = float(np.std(r))
    if r_std > 0:
        corr_t = float(np.corrcoef(t, r)[0, 1]) if float(np.std(t)) > 0 else 0.0
        corr_m = float(np.corrcoef(m, r)[0, 1]) if float(np.std(m)) > 0 else 0.0
        corr_v = float(np.corrcoef(v, r)[0, 1]) if float(np.std(v)) > 0 else 0.0
    else:
        corr_t = corr_m = corr_v = 0.0

    corr_t = max(corr_t, 0.0)
    corr_m = max(corr_m, 0.0)
    corr_v = max(corr_v, 0.0)

    total = corr_t + corr_m + corr_v
    if total > 0:
        w_trend[i] = corr_t / total
        w_momentum[i] = corr_m / total
        w_reversion[i] = corr_v / total
    else:
        w_trend[i] = w_momentum[i] = w_reversion[i] = 1.0 / 3.0

# Weighted composite
composite = w_trend * trend_score + w_momentum * momentum_score + w_reversion * reversion_score

plot(composite, title="Neural Weight", color=color.blue)
hline(0, title="Zero", color=color.gray)
hline(0.5, title="Upper", color=color.red)
hline(-0.5, title="Lower", color=color.green)
bgcolor(composite > 0.5, color="rgba(0,255,0,0.1)")
bgcolor(composite < -0.5, color="rgba(255,0,0,0.1)")
