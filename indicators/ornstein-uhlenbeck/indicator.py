from tg_scripting import *
import numpy as np

try:
    from scipy.stats import linregress
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

indicator("Ornstein-Uhlenbeck Estimator", overlay=False)

length = input.int(60, "Lookback Length", minval=20, maxval=300)
show_eq = input.bool(True, "Show Equilibrium Level")

c = np.array(close, dtype=float)
n = len(c)

theta = np.full(n, np.nan)
mu_eq = np.full(n, np.nan)
sigma_ou = np.full(n, np.nan)
z_score = np.full(n, np.nan)

dt = 1.0

for i in range(length - 1, n):
    window = c[i - length + 1:i + 1]
    x = window[:-1]
    y = window[1:]
    if HAS_SCIPY:
        result = linregress(x, y)
        a = result.intercept
        b = result.slope
    else:
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        num = np.sum((x - x_mean) * (y - y_mean))
        den = np.sum((x - x_mean) ** 2)
        b = num / den if abs(den) > 1e-10 else 1.0
        a = y_mean - b * x_mean

    if b < 1.0 - 1e-6:
        theta_val = -np.log(max(b, 1e-10)) / dt
        mu_val = a / (1.0 - b)
        residuals = y - (a + b * x)
        sig = np.std(residuals)
        theta[i] = min(theta_val, 10.0)
        mu_eq[i] = mu_val
        sigma_ou[i] = sig
        eq_std = sig / np.sqrt(2.0 * theta_val) if theta_val > 1e-10 else sig
        if eq_std > 1e-10:
            z_score[i] = (c[i] - mu_val) / eq_std

strong_rev = np.array([not np.isnan(theta[i]) and theta[i] > 0.5 for i in range(n)])
overbought = np.array([not np.isnan(z_score[i]) and z_score[i] > 2.0 for i in range(n)])
oversold = np.array([not np.isnan(z_score[i]) and z_score[i] < -2.0 for i in range(n)])

plot(theta, title="Mean-Rev Speed", color="#42A5F5", linewidth=2)
plot(z_score, title="Z-Score", color="#FF9800", linewidth=1)
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
hline(0.5, title="Strong Reversion", color="#66BB6A", linestyle="dashed")
hline(2.0, title="Overbought", color="#EF5350", linestyle="dashed")
hline(-2.0, title="Oversold", color="#66BB6A", linestyle="dashed")
bgcolor(overbought, color="rgba(244,67,54,0.08)")
bgcolor(oversold, color="rgba(76,175,80,0.08)")
