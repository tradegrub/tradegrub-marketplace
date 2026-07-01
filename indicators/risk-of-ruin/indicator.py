from tg_scripting import *
import numpy as np

indicator("Risk of Ruin Calculator", overlay=False)

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
risk_pct = input.float(2.0, "Risk Per Trade %", minval=0.1, maxval=10.0, step=0.1)
ruin_level = input.float(50.0, "Ruin Level %", minval=10.0, maxval=90.0, step=5.0)
num_sims = input.int(100, "Simulations", minval=20, maxval=500)

n = len(close)
ror = np.zeros(n)
win_rate_arr = np.zeros(n)
survival = np.zeros(n)
danger = np.zeros(n, dtype=bool)

ruin_thresh = 1.0 - ruin_level / 100.0

for i in range(lookback, n):
    returns = []
    for j in range(i - lookback + 1, i + 1):
        r = (close[j] - close[j - 1]) / close[j - 1] if j > 0 else 0
        returns.append(r)

    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    wr = len(wins) / len(returns) if returns else 0
    win_rate_arr[i] = wr * 100.0

    ruin_count = 0
    trade_risk = risk_pct / 100.0
    for s in range(num_sims):
        equity = 1.0
        np.random.seed(i * num_sims + s)
        for t in range(lookback):
            idx = np.random.randint(0, len(returns))
            r = returns[idx]
            equity *= (1.0 + r * trade_risk / max(abs(r), 1e-8) if abs(r) > 0 else 1.0)
            equity = max(equity, 0)
            if equity <= ruin_thresh:
                ruin_count += 1
                break

    ror[i] = ruin_count / num_sims * 100.0
    survival[i] = 100.0 - ror[i]
    danger[i] = ror[i] > 25.0

plot(ror, title="Risk of Ruin %", color="#ff5252", linewidth=2)
plot(survival, title="Survival %", color="#00e676", linewidth=1)
plot(win_rate_arr, title="Win Rate %", color="#42a5f5", linewidth=1)
hline(25, title="Danger", color="#ff5252", linestyle="dashed")
hline(50, title="Midpoint", color="#555555", linestyle="dashed")
bgcolor(danger, color="rgba(255,82,82,0.06)")
