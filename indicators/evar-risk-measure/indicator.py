from tg_scripting import *
import numpy as np
from scipy import stats

indicator("Entropy Risk Measure", overlay=False)

lookback = input.int(50, "Lookback", minval=20, maxval=200)
confidence = input.float(95.0, "Confidence %", minval=90.0, maxval=99.9, step=0.5)
risk_budget = input.float(2.0, "Risk Budget %", minval=0.5, maxval=10.0, step=0.5)

cl = np.array(close, dtype=float)
n = len(cl)

log_returns = np.zeros(n)
log_returns[1:] = np.log(cl[1:] / np.where(cl[:-1] > 0, cl[:-1], 1.0))

z = stats.norm.ppf(1 - confidence / 100)

evar = np.zeros(n)
pos_size = np.zeros(n)

for i in range(lookback, n):
    window = log_returns[i - lookback + 1:i + 1]
    std = np.std(window, ddof=1)
    if std <= 0:
        continue

    traditional_var = -z * std

    skew = float(stats.skew(window))
    kurt = float(stats.kurtosis(window, fisher=True))

    z_val = -z
    cf_adjustment = 1 + (skew / 6) * (z_val ** 2 - 1) + (kurt / 24) * (z_val ** 3 - 3 * z_val)
    evar[i] = traditional_var * cf_adjustment * 100

    if evar[i] > 0:
        pos_size[i] = risk_budget / evar[i] * 100

evar_clipped = np.clip(evar, 0, 20)
pos_clipped = np.clip(pos_size, 0, 500)

high_risk = evar_clipped > 5

plot(evar_clipped.tolist(), title="EVaR %", color="#f44336", linewidth=2)
plot(pos_clipped.tolist(), title="Position Size %", color="#26c6da", linewidth=1)
hline(2, title="Normal Risk", color="#4CAF50", linestyle="dashed")
hline(5, title="Elevated Risk", color="#ff9800", linestyle="dashed")
hline(100, title="Full Size", color="#888888", linestyle="dashed")
bgcolor(high_risk.tolist(), color="rgba(244,67,54,0.06)")
