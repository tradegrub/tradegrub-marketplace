from tg_scripting import *
import numpy as np

try:
    from scipy.stats import norm
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

indicator("Value at Risk Estimator", overlay=False)

length = input.int(60, "Lookback Length", minval=20, maxval=500)
confidence = input.float(95.0, "Confidence %", minval=90.0, maxval=99.9, step=0.5)
method = input.int(0, "Method (0=Parametric 1=Historical)", minval=0, maxval=1)

c = np.array(close, dtype=float)
n = len(c)

returns = np.diff(np.log(np.maximum(c, 1e-10)))
returns = np.concatenate([[0.0], returns])

var_pct = np.full(n, np.nan)
conf_level = confidence / 100.0

if HAS_SCIPY:
    z_score = norm.ppf(1.0 - conf_level)
else:
    z_table = {0.90: -1.2816, 0.95: -1.6449, 0.975: -1.96, 0.99: -2.3263, 0.999: -3.0902}
    z_score = z_table.get(conf_level, -1.6449)

for i in range(length, n):
    window = returns[i - length + 1:i + 1]
    if method == 0:
        mu = np.mean(window)
        sigma = np.std(window)
        var_pct[i] = (mu + z_score * sigma) * 100.0
    else:
        sorted_ret = np.sort(window)
        idx = int(np.floor((1.0 - conf_level) * len(sorted_ret)))
        idx = max(0, min(idx, len(sorted_ret) - 1))
        var_pct[i] = sorted_ret[idx] * 100.0

var_dollar = np.full(n, np.nan)
for i in range(length, n):
    if not np.isnan(var_pct[i]):
        var_dollar[i] = c[i] * var_pct[i] / 100.0

breach = np.array([False] * n)
for i in range(length + 1, n):
    if not np.isnan(var_pct[i - 1]) and returns[i] * 100.0 < var_pct[i - 1]:
        breach[i] = True

plot(var_pct, title="VaR %", color="#EF5350", linewidth=2)
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(breach, color="rgba(244,67,54,0.15)")
plotshape(breach, title="VaR Breach", style="triangledown", location="belowbar", color="#EF5350")
