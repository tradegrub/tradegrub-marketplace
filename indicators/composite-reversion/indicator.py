from tg_scripting import *
import numpy as np

indicator("Composite Reversion Score", overlay=False)

lookback = input.int(50, "Lookback", minval=10, maxval=200)

cl = np.array(close, dtype=float)
n = len(cl)

composite = np.full(n, 50.0)

for i in range(lookback, n):
    window = cl[i - lookback:i + 1]

    # 1. Momentum percentile: percentile rank of current ROC
    roc_vals = np.zeros(lookback)
    for j in range(1, lookback + 1):
        idx = i - lookback + j
        roc_vals[j - 1] = (cl[idx] - cl[idx - 1]) / cl[idx - 1] * 100.0 if cl[idx - 1] > 0 else 0.0
    current_roc = roc_vals[-1]
    momentum_pct = float(np.sum(roc_vals <= current_roc)) / len(roc_vals) * 100.0

    # 2. Streak: consecutive up/down bars normalized
    streak = 0
    for j in range(i, max(i - lookback, 0), -1):
        if cl[j] > cl[j - 1]:
            if streak >= 0:
                streak += 1
            else:
                break
        elif cl[j] < cl[j - 1]:
            if streak <= 0:
                streak -= 1
            else:
                break
        else:
            break
    # Normalize streak to 0-100 (max streak ~lookback/2)
    max_streak = lookback / 2.0
    streak_norm = (streak / max_streak + 1.0) / 2.0 * 100.0
    streak_norm = np.clip(streak_norm, 0.0, 100.0)

    # 3. Return percentile: percentile rank of N-bar return
    n_bar_returns = np.zeros(lookback)
    for j in range(lookback):
        idx = i - lookback + j + 1
        start_idx = max(idx - 10, 0)
        n_bar_returns[j] = (cl[idx] - cl[start_idx]) / cl[start_idx] * 100.0 if cl[start_idx] > 0 else 0.0
    current_return = n_bar_returns[-1]
    return_pct = float(np.sum(n_bar_returns <= current_return)) / len(n_bar_returns) * 100.0

    # Composite: average of all three
    composite[i] = (momentum_pct + streak_norm + return_pct) / 3.0

overbought = (composite > 80.0).tolist()
oversold = (composite < 20.0).tolist()

plot(composite.tolist(), title="Composite Score", color="#7E57C2")
hline(80, title="Overbought", color="#EF5350")
hline(20, title="Oversold", color="#26A69A")
hline(50, title="Neutral", color="#555555")
bgcolor(overbought, color="rgba(239,83,80,0.08)")
bgcolor(oversold, color="rgba(38,166,154,0.08)")
