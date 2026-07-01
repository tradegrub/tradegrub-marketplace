from tg_scripting import *
import numpy as np
import pandas as pd

indicator("Percentile Momentum Ranker", overlay=False)

lookback = input.int(20, "Ranking Window", minval=5, maxval=100)
fast_period = input.int(5, "Fast Momentum", minval=2, maxval=20)
slow_period = input.int(20, "Slow Momentum", minval=10, maxval=50)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)
show_zones = input.bool(True, "Show Rank Zones")

df = pd.DataFrame({'close': close, 'high': high, 'low': low, 'volume': volume})

df['fast_ret'] = df['close'].pct_change(fast_period)
df['slow_ret'] = df['close'].pct_change(slow_period)
df['vol_ratio'] = df['volume'] / df['volume'].rolling(lookback).mean()
df['range_pct'] = (df['high'] - df['low']) / df['close']

df['fast_rank'] = df['fast_ret'].rolling(lookback).rank(pct=True)
df['slow_rank'] = df['slow_ret'].rolling(lookback).rank(pct=True)
df['vol_rank'] = df['vol_ratio'].rolling(lookback).rank(pct=True)

composite = (df['fast_rank'] * 0.4 + df['slow_rank'] * 0.4 + df['vol_rank'] * 0.2) * 100
momentum_rank = composite.rolling(smooth).mean().to_numpy()

plot(momentum_rank, title="Momentum Rank", color="blue", linewidth=2)
hline(75, title="Strong", color="green")
hline(50, title="Neutral", color="gray")
hline(25, title="Weak", color="red")

if show_zones:
    bgcolor(momentum_rank > 75, color="#00e676")
    bgcolor(momentum_rank < 25, color="#ff1744")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)
last_label_idx = -100
cooldown = 20

for i in range(lookback + smooth, n):
    if not show_labels:
        break
    if np.isnan(momentum_rank[i]):
        continue
    if (i - last_label_idx) <= cooldown:
        continue

    # Zone entry labels
    if i > 0 and not np.isnan(momentum_rank[i - 1]):
        if momentum_rank[i] > 75 and momentum_rank[i - 1] <= 75:
            last_label_idx = i
            label.new(
                x=i, y=float(momentum_rank[i]),
                text="Strong Momentum",
                style=label.style_label_down,
                color="rgba(0,230,118,0.3)",
                textcolor="#00e676",
                size="small"
            )
        elif momentum_rank[i] < 25 and momentum_rank[i - 1] >= 25:
            last_label_idx = i
            label.new(
                x=i, y=float(momentum_rank[i]),
                text="Weak Momentum",
                style=label.style_label_up,
                color="rgba(255,23,68,0.3)",
                textcolor="#ff1744",
                size="small"
            )
        elif momentum_rank[i] > 50 and momentum_rank[i - 1] <= 50:
            last_label_idx = i
            label.new(
                x=i, y=float(momentum_rank[i]),
                text="Above Neutral",
                style=label.style_label_up,
                color="rgba(66,165,245,0.2)",
                textcolor="#42a5f5",
                size="tiny"
            )
        elif momentum_rank[i] < 50 and momentum_rank[i - 1] >= 50:
            last_label_idx = i
            label.new(
                x=i, y=float(momentum_rank[i]),
                text="Below Neutral",
                style=label.style_label_down,
                color="rgba(136,136,136,0.2)",
                textcolor="#888888",
                size="tiny"
            )
