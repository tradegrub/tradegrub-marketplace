from tg_scripting import *
import numpy as np

try:
    from scipy.stats import norm
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

indicator("Conditional VaR (Expected Shortfall)", overlay=False)

length = input.int(60, "Lookback Length", minval=20, maxval=500)
confidence = input.float(95.0, "Confidence %", minval=90.0, maxval=99.9, step=0.5)

c = np.array(close, dtype=float)
n = len(c)

returns = np.diff(np.log(np.maximum(c, 1e-10)))
returns = np.concatenate([[0.0], returns])

var_pct = np.full(n, np.nan)
cvar_pct = np.full(n, np.nan)
conf_level = confidence / 100.0

for i in range(length, n):
    window = returns[i - length + 1:i + 1]
    sorted_ret = np.sort(window)
    cutoff_idx = int(np.floor((1.0 - conf_level) * len(sorted_ret)))
    cutoff_idx = max(1, min(cutoff_idx, len(sorted_ret) - 1))
    var_pct[i] = sorted_ret[cutoff_idx] * 100.0
    tail = sorted_ret[:cutoff_idx]
    if len(tail) > 0:
        cvar_pct[i] = np.mean(tail) * 100.0
    else:
        cvar_pct[i] = var_pct[i]

tail_ratio = np.full(n, np.nan)
for i in range(length, n):
    if not np.isnan(var_pct[i]) and abs(var_pct[i]) > 1e-10:
        tail_ratio[i] = cvar_pct[i] / var_pct[i]

breach = np.array([False] * n)
for i in range(length + 1, n):
    if not np.isnan(cvar_pct[i - 1]) and returns[i] * 100.0 < cvar_pct[i - 1]:
        breach[i] = True

plot(var_pct, title="VaR %", color="#FF9800", linewidth=1)
plot(cvar_pct, title="CVaR %", color="#EF5350", linewidth=2)
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(breach, color="rgba(244,67,54,0.15)")
plotshape(breach, title="Tail Breach", style="triangledown", location="belowbar", color="#EF5350")
