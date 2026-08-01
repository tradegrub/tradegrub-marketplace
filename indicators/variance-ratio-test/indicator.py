from tg_scripting import *
import numpy as np

indicator("Variance Ratio Test", overlay=False)

short_period = input.int(5, "Short Period", minval=2, maxval=50)
long_period = input.int(20, "Long Period", minval=10, maxval=200)
smooth = input.int(10, "Smoothing", minval=1, maxval=50)
upper_thresh = input.float(1.5, "Random Walk Upper", minval=1.0, maxval=3.0, step=0.1)
lower_thresh = input.float(0.5, "Mean Reversion Lower", minval=0.1, maxval=1.0, step=0.1)

src = np.array(close, dtype=float)
n = len(src)
log_ret = np.diff(np.log(np.where(src > 0, src, 1.0)))
log_ret = np.concatenate([[0.0], log_ret])

vr = np.full(n, 1.0)
for i in range(long_period, n):
    short_rets = log_ret[i - long_period:i]
    var_1 = np.var(short_rets)
    if var_1 == 0:
        vr[i] = 1.0
        continue
    q = long_period // short_period
    agg_rets = np.array([np.sum(short_rets[j:j + q]) for j in range(0, len(short_rets) - q + 1, q)])
    var_q = np.var(agg_rets)
    vr[i] = (var_q / (q * var_1)) if q * var_1 != 0 else 1.0

vr_smooth = ta.sma(vr.tolist(), smooth)

trend_score = np.where(np.array(vr_smooth) > upper_thresh, 1.0, np.where(np.array(vr_smooth) < lower_thresh, -1.0, 0.0))
is_trending = np.array(vr_smooth) > upper_thresh
is_reverting = np.array(vr_smooth) < lower_thresh

plot(vr_smooth, title="Variance Ratio", color="#42A5F5", linewidth=2)
hline(1.0, title="Random Walk", color="#888888", linestyle="dashed")
hline(upper_thresh, title="Trending", color="#66BB6A", linestyle="dashed")
hline(lower_thresh, title="Mean Reverting", color="#EF5350", linestyle="dashed")
bgcolor(is_trending, color="rgba(102,187,106,0.08)")
bgcolor(is_reverting, color="rgba(239,83,80,0.08)")
plot(trend_score, title="Regime", color="#FFD54F", linewidth=1)
