from tg_scripting import *
import numpy as np

indicator("Bar Behavior Analysis", overlay=False)

lookback = input.int(100, "Lookback Period", minval=20, maxval=500)
bar_type_filter = input.bool(True, "Filter by Bar Type")

cl = np.array(close, dtype=float)
op = np.array(open, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

# Classify each bar: 1=bullish, -1=bearish, 0=doji
body = cl - op
avg_range = np.zeros(n)
alpha = 2.0 / (21)
for i in range(1, n):
    avg_range[i] = alpha * (hi[i] - lo[i]) + (1 - alpha) * avg_range[i - 1]
avg_range[0] = hi[0] - lo[0]

doji_thresh = avg_range * 0.1
bar_class = np.zeros(n, dtype=int)
for i in range(n):
    if body[i] > doji_thresh[i]:
        bar_class[i] = 1
    elif body[i] < -doji_thresh[i]:
        bar_class[i] = -1
    else:
        bar_class[i] = 0

# Relative bar size: small (0), medium (1), large (2)
bar_size = np.zeros(n, dtype=int)
for i in range(n):
    r = hi[i] - lo[i]
    if avg_range[i] > 0:
        ratio = r / avg_range[i]
        if ratio < 0.6:
            bar_size[i] = 0
        elif ratio > 1.4:
            bar_size[i] = 2
        else:
            bar_size[i] = 1

# Calculate probabilities using rolling window of similar bars
bull_prob = np.full(n, 50.0)
bear_prob = np.full(n, 50.0)
follow_through = np.zeros(n)

for i in range(lookback + 1, n):
    start = max(0, i - lookback)
    bull_count = 0
    bear_count = 0
    total_match = 0
    ft_sum = 0.0

    current_class = bar_class[i]
    current_size = bar_size[i]

    for j in range(start, i - 1):
        # Match criteria
        if bar_type_filter:
            if bar_class[j] != current_class or bar_size[j] != current_size:
                continue

        total_match += 1
        next_body = cl[j + 1] - op[j + 1]
        next_range = hi[j + 1] - lo[j + 1]

        if next_body > 0:
            bull_count += 1
        elif next_body < 0:
            bear_count += 1

        if next_range > 0:
            ft_sum += abs(next_body) / next_range

    if total_match >= 5:
        bull_prob[i] = (bull_count / total_match) * 100.0
        bear_prob[i] = (bear_count / total_match) * 100.0
        follow_through[i] = (ft_sum / total_match) * 100.0
    else:
        bull_prob[i] = 50.0
        bear_prob[i] = 50.0
        follow_through[i] = 50.0

# Plot bullish probability as green area, bearish as red area
bull_above = np.where(bull_prob > 50, bull_prob, 50.0)
bear_above = np.where(bear_prob > 50, bear_prob, 50.0)

plot(bull_prob.tolist(), title="Bullish Probability", color="#4CAF50", linewidth=1)
fill_between = bull_prob > 50
bgcolor(fill_between.tolist(), color="rgba(76,175,80,0.12)")

plot(bear_prob.tolist(), title="Bearish Probability", color="#f44336", linewidth=1)
fill_bearish = bear_prob > 50
bgcolor(fill_bearish.tolist(), color="rgba(244,67,54,0.12)")

plot(follow_through.tolist(), title="Follow-Through Strength", color="#ffab00", linewidth=2)

hline(50, title="Neutral", color="#888888", linestyle="dashed")
hline(70, title="Strong Signal", color="#666666", linestyle="dotted")
hline(30, title="Weak Signal", color="#666666", linestyle="dotted")
