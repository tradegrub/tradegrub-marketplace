from tg_scripting import *
import numpy as np

indicator("Volatility Ratio", overlay=False)

short_len = input.int(5, "Short Length", minval=2, maxval=50)
long_len = input.int(20, "Long Length", minval=10, maxval=200)
thresh_high = input.float(1.5, "Expansion Threshold", minval=1.0, maxval=5.0, step=0.1)
thresh_low = input.float(0.7, "Contraction Threshold", minval=0.1, maxval=1.0, step=0.1)

c = np.array(close, dtype=float)
n = len(c)

returns = np.diff(np.log(np.maximum(c, 1e-10)))
returns = np.concatenate([[0.0], returns])

short_vol = np.full(n, np.nan)
long_vol = np.full(n, np.nan)
ratio = np.full(n, np.nan)

for i in range(long_len, n):
    sv = np.std(returns[i - short_len + 1:i + 1])
    lv = np.std(returns[i - long_len + 1:i + 1])
    short_vol[i] = sv
    long_vol[i] = lv
    ratio[i] = sv / max(lv, 1e-10)

expanding = np.array([not np.isnan(ratio[i]) and ratio[i] > thresh_high for i in range(n)])
contracting = np.array([not np.isnan(ratio[i]) and ratio[i] < thresh_low for i in range(n)])

plot(ratio, title="Vol Ratio", color="#42A5F5", linewidth=2)
hline(1.0, title="Neutral", color="#888888", linestyle="dashed")
hline(thresh_high, title="Expansion", color="#EF5350", linestyle="dashed")
hline(thresh_low, title="Contraction", color="#66BB6A", linestyle="dashed")
bgcolor(expanding, color="rgba(244,67,54,0.08)")
bgcolor(contracting, color="rgba(76,175,80,0.08)")
