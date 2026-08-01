from tg_scripting import *
import numpy as np

try:
    from scipy.stats import linregress
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

indicator("Half-Life Mean Reversion", overlay=False)

length = input.int(60, "Lookback Length", minval=20, maxval=300)
ma_len = input.int(20, "Mean Length", minval=5, maxval=100)

c = np.array(close, dtype=float)
n = len(c)

ma = np.full(n, np.nan)
for i in range(ma_len - 1, n):
    ma[i] = np.mean(c[i - ma_len + 1:i + 1])

spread = c - ma
half_life = np.full(n, np.nan)

for i in range(length - 1, n):
    s = spread[i - length + 1:i + 1]
    valid = ~np.isnan(s)
    sv = s[valid]
    if len(sv) < 10:
        continue
    y = np.diff(sv)
    x = sv[:-1]
    if len(x) < 5:
        continue
    if HAS_SCIPY:
        result = linregress(x, y)
        beta = result.slope
    else:
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        num = np.sum((x - x_mean) * (y - y_mean))
        den = np.sum((x - x_mean) ** 2)
        beta = num / den if abs(den) > 1e-10 else 0.0
    if beta < -1e-10:
        hl = -np.log(2.0) / beta
        half_life[i] = min(hl, 200.0)

norm_spread = np.full(n, np.nan)
for i in range(ma_len - 1, n):
    window = spread[max(0, i - length + 1):i + 1]
    valid = window[~np.isnan(window)]
    if len(valid) > 1:
        std = np.std(valid)
        if std > 1e-10:
            norm_spread[i] = spread[i] / std

fast_rev = np.array([not np.isnan(half_life[i]) and half_life[i] < 10.0 for i in range(n)])

plot(half_life, title="Half-Life (bars)", color="#42A5F5", linewidth=2)
plot(norm_spread, title="Norm Spread", color="#FF9800", linewidth=1)
hline(0.0, title="Zero Spread", color="#888888", linestyle="dashed")
hline(10.0, title="Fast Reversion", color="#66BB6A", linestyle="dashed")
bgcolor(fast_rev, color="rgba(76,175,80,0.08)")
