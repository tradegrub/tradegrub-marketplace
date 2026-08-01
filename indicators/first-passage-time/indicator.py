from tg_scripting import *
import numpy as np
from scipy.special import erfc

indicator("First Passage Time Estimator", overlay=False)

target_pct = input.float(5.0, "Target Percent", minval=1.0, maxval=20.0, step=0.5)
lookback = input.int(50, "Lookback", minval=10, maxval=200)

src = np.array(close, dtype=float)
n = len(src)

log_returns = np.diff(np.log(src), prepend=0.0)

prob_upper = np.zeros(n)
prob_lower = np.zeros(n)

for i in range(lookback, n):
    window = log_returns[i - lookback + 1:i + 1]
    mu = np.mean(window)
    sigma = np.std(window)

    if sigma <= 0:
        prob_upper[i] = 0.0
        prob_lower[i] = 0.0
        continue

    # Log barrier distances
    b_upper = np.log(1.0 + target_pct / 100.0)
    b_lower = np.log(1.0 - target_pct / 100.0)

    # First passage probability over lookback horizon
    # P(max S > barrier) using reflection principle for GBM
    # P = erfc((b - mu*T) / (sigma*sqrt(2*T))) + exp(2*mu*b/sigma^2) * erfc((b + mu*T) / (sigma*sqrt(2*T)))
    T = float(lookback)
    sqrt_2T = np.sqrt(2.0 * T)

    # Upper barrier
    d1u = (b_upper - mu * T) / (sigma * sqrt_2T)
    d2u = (b_upper + mu * T) / (sigma * sqrt_2T)
    exp_term_u = np.exp(min(2.0 * mu * b_upper / (sigma ** 2), 50.0))
    p_up = float(0.5 * erfc(d1u) + exp_term_u * 0.5 * erfc(d2u))
    prob_upper[i] = min(100.0, max(0.0, p_up * 100.0))

    # Lower barrier (use absolute value of log barrier)
    b_low_abs = abs(b_lower)
    d1l = (b_low_abs + mu * T) / (sigma * sqrt_2T)
    d2l = (b_low_abs - mu * T) / (sigma * sqrt_2T)
    exp_term_l = np.exp(min(-2.0 * mu * b_low_abs / (sigma ** 2), 50.0))
    p_down = float(0.5 * erfc(d1l) + exp_term_l * 0.5 * erfc(d2l))
    prob_lower[i] = min(100.0, max(0.0, p_down * 100.0))

plot(prob_upper.tolist(), title="Upper Target Probability", color="#4CAF50", linewidth=2)
plot(prob_lower.tolist(), title="Lower Target Probability", color="#EF5350", linewidth=2)
hline(50, title="50% Level", color="#FFA726", linestyle="dashed")
