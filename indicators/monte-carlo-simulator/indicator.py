from tg_scripting import *
import numpy as np

indicator("Monte Carlo Equity Simulator", overlay=False)

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
num_sims = input.int(100, "Simulations", minval=20, maxval=500)
conf_level = input.float(95.0, "Confidence %", minval=50.0, maxval=99.0, step=5.0)

n = len(close)
median_eq = np.full(n, 100.0)
upper_bound = np.full(n, 100.0)
lower_bound = np.full(n, 100.0)
actual_eq = np.full(n, 100.0)
spread = np.zeros(n)

for i in range(1, n):
    actual_eq[i] = actual_eq[i - 1] * (1.0 + (close[i] - close[i - 1]) / close[i - 1])

for i in range(lookback, n):
    returns = []
    for j in range(i - lookback + 1, i + 1):
        returns.append((close[j] - close[j - 1]) / close[j - 1])

    final_vals = []
    proj_len = min(20, n - i)
    for s in range(num_sims):
        eq = actual_eq[i]
        np.random.seed(i * num_sims + s)
        for t in range(proj_len):
            idx = np.random.randint(0, len(returns))
            eq *= (1.0 + returns[idx])
        final_vals.append(eq)

    final_vals.sort()
    lo_idx = int((100 - conf_level) / 200.0 * len(final_vals))
    hi_idx = int((1 - (100 - conf_level) / 200.0) * len(final_vals)) - 1
    lo_idx = max(0, min(lo_idx, len(final_vals) - 1))
    hi_idx = max(0, min(hi_idx, len(final_vals) - 1))

    median_eq[i] = final_vals[len(final_vals) // 2]
    lower_bound[i] = final_vals[lo_idx]
    upper_bound[i] = final_vals[hi_idx]
    spread[i] = upper_bound[i] - lower_bound[i]

plot(actual_eq, title="Actual Equity", color="#42a5f5", linewidth=2)
plot(median_eq, title="Median Path", color="#ffa726", linewidth=1)
plot(upper_bound, title="Upper Bound", color="#00e676", linewidth=1)
plot(lower_bound, title="Lower Bound", color="#ff5252", linewidth=1)

wide = np.array([spread[i] > np.mean(spread[lookback:]) * 1.5 if i >= lookback else False for i in range(n)], dtype=bool)
bgcolor(wide, color="rgba(255,193,7,0.06)")
