from tg_scripting import *
import numpy as np

indicator("Bollinger Width Percentile", overlay=False)

bb_len = input.int(20, "BB Length", minval=5, maxval=200)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=5.0, step=0.5)
pct_len = input.int(100, "Percentile Lookback", minval=20, maxval=500)
squeeze_thresh = input.float(20.0, "Squeeze Threshold %", minval=5.0, maxval=50.0, step=5.0)
expansion_thresh = input.float(80.0, "Expansion Threshold %", minval=50.0, maxval=95.0, step=5.0)

upper, middle, lower = ta.bb(close, bb_len, bb_mult)

bw = np.array(upper, dtype=float) - np.array(lower, dtype=float)
mid = np.array(middle, dtype=float)
bw_pct = bw / np.maximum(mid, 1e-10) * 100.0

n = len(close)
percentile = np.full(n, np.nan)

for i in range(pct_len - 1, n):
    window = bw_pct[i - pct_len + 1:i + 1]
    valid = window[~np.isnan(window)]
    if len(valid) > 0:
        rank = np.sum(valid <= bw_pct[i])
        percentile[i] = (rank / len(valid)) * 100.0

is_squeeze = np.array([not np.isnan(percentile[i]) and percentile[i] < squeeze_thresh for i in range(n)])
is_expansion = np.array([not np.isnan(percentile[i]) and percentile[i] > expansion_thresh for i in range(n)])

plot(percentile, title="Width Percentile", color="#42A5F5", linewidth=2)
hline(squeeze_thresh, title="Squeeze", color="#66BB6A", linestyle="dashed")
hline(expansion_thresh, title="Expansion", color="#EF5350", linestyle="dashed")
hline(50.0, title="Median", color="#888888", linestyle="dashed")
bgcolor(is_squeeze, color="rgba(76,175,80,0.08)")
bgcolor(is_expansion, color="rgba(244,67,54,0.08)")
