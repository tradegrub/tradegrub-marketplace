from tg_scripting import *
import numpy as np

indicator("Kelly Criterion Sizer", overlay=False)

lookback = input.int(50, "Lookback Trades", minval=10, maxval=200)
fraction = input.float(0.5, "Kelly Fraction", minval=0.1, maxval=1.0, step=0.1)
threshold = input.float(0.0, "Min Kelly to Show", minval=0.0, maxval=0.5, step=0.05)

n = len(close)
wins = np.zeros(n)
losses = np.zeros(n)
win_rate = np.zeros(n)
avg_win = np.zeros(n)
avg_loss = np.zeros(n)
kelly_pct = np.zeros(n)
half_kelly = np.zeros(n)

for i in range(1, n):
    changes = []
    start = max(1, i - lookback + 1)
    for j in range(start, i + 1):
        changes.append((close[j] - close[j - 1]) / close[j - 1])

    w = [c for c in changes if c > 0]
    l = [abs(c) for c in changes if c < 0]

    if len(w) > 0 and len(l) > 0:
        wr = len(w) / len(changes)
        aw = np.mean(w)
        al = np.mean(l)
        win_rate[i] = wr * 100.0
        avg_win[i] = aw * 100.0
        avg_loss[i] = al * 100.0

        payoff = aw / al if al > 0 else 0
        k = wr - (1 - wr) / payoff if payoff > 0 else 0
        kelly_pct[i] = max(0, k * 100.0)
        half_kelly[i] = max(0, k * fraction * 100.0)

plot(kelly_pct, title="Full Kelly %", color="#42a5f5", linewidth=2)
plot(half_kelly, title="Fractional Kelly %", color="#00e676", linewidth=2)
plot(win_rate, title="Win Rate %", color="#ffa726", linewidth=1)
hline(0, title="Zero", color="#555555", linestyle="dashed")
hline(25, title="25% Size", color="#333333", linestyle="dashed")

over_bet = np.array([kelly_pct[i] > 50 for i in range(n)], dtype=bool)
bgcolor(over_bet, color="rgba(255,82,82,0.08)")
