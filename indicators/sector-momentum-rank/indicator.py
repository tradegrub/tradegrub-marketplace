from tg_scripting import *
import numpy as np

indicator("Momentum Rank", overlay=False)

lookback = input.int(200, "Lookback", minval=50, maxval=500)

src = np.array(close, dtype=float)
n = len(src)

# Multi-timeframe return periods
periods = [5, 10, 20, 50, 100]
weights = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
weights = weights / weights.sum()

composite = np.full(n, np.nan)

for i in range(lookback, n):
    ranks = []
    for p in periods:
        if i >= p:
            # Current return
            current_ret = (src[i] - src[i - p]) / src[i - p] if src[i - p] != 0 else 0.0

            # Historical returns over lookback for percentile ranking
            start = max(p, i - lookback)
            hist_returns = np.array([
                (src[j] - src[j - p]) / src[j - p] if src[j - p] != 0 else 0.0
                for j in range(start, i + 1)
            ])

            # Percentile rank: fraction of historical returns below current
            rank = np.sum(hist_returns <= current_ret) / len(hist_returns) * 100.0
            ranks.append(rank)
        else:
            ranks.append(50.0)

    ranks = np.array(ranks)
    composite[i] = np.sum(ranks * weights)

# Smooth slightly
smoothed = np.array(ta.sma(composite.tolist(), 3), dtype=float)

# Direction coloring
colors = np.where(smoothed > 50, "#4CAF50", "#f44336").tolist()

plot(smoothed.tolist(), title="Momentum Rank", color=colors)
hline(80, title="Overbought", color="#f44336")
hline(20, title="Oversold", color="#4CAF50")
hline(50, title="Neutral", color="#888888")
bgcolor(smoothed > 80, color="rgba(76,175,80,0.08)")
bgcolor(smoothed < 20, color="rgba(244,67,54,0.08)")
