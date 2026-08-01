from tg_scripting import *
import numpy as np

indicator("Market Criticality Index", overlay=False)

length = input.int(50, "Lookback Length", minval=10, maxval=200)
tail_thresh = input.float(2.0, "Tail Threshold (Std Devs)", minval=1.0, maxval=4.0, step=0.5)

src = np.array(close, dtype=float)
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
n = len(src)

returns = np.diff(np.log(src), prepend=0.0)

criticality = np.zeros(n)

for i in range(length, n):
    window = returns[i - length + 1:i + 1]
    mu = np.mean(window)
    sigma = np.std(window)

    # Tail risk: fraction of returns beyond threshold std devs
    if sigma > 0:
        tail_count = np.sum(np.abs(window - mu) > tail_thresh * sigma)
        tail_risk = float(tail_count) / length
    else:
        tail_risk = 0.0

    # Volatility clustering: autocorrelation of squared returns
    sq = window ** 2
    sq_mean = np.mean(sq)
    sq_var = np.var(sq)
    if sq_var > 0:
        autocorr = float(np.mean((sq[1:] - sq_mean) * (sq[:-1] - sq_mean)) / sq_var)
        vol_cluster = max(0.0, autocorr)
    else:
        vol_cluster = 0.0

    # Range compression: current range vs average range
    hi_win = h[i - length + 1:i + 1]
    lo_win = l[i - length + 1:i + 1]
    ranges = hi_win - lo_win
    avg_range = np.mean(ranges)
    curr_range = float(ranges[-1])
    if avg_range > 0:
        range_comp = 1.0 - min(1.0, curr_range / avg_range)
    else:
        range_comp = 0.0

    # Combine into 0-100 score
    raw = (tail_risk * 40.0 + vol_cluster * 30.0 + range_comp * 30.0)
    criticality[i] = min(100.0, max(0.0, raw * 100.0))

# Smooth
kern = np.ones(3) / 3
criticality_smooth = np.convolve(criticality, kern, mode='same')

is_critical = criticality_smooth > 70.0

plot(criticality_smooth.tolist(), title="Criticality Index", color="#EF5350", linewidth=2)
hline(70, title="Danger Zone", color="#FFA726", linestyle="dashed")
hline(30, title="Stable Zone", color="#4CAF50", linestyle="dashed")
bgcolor(is_critical.tolist(), color="rgba(239,83,80,0.15)")
