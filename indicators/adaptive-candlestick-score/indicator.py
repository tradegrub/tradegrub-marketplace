from tg_scripting import *
import numpy as np

lookback = input.int(200, "Lookback", minval=50, maxval=500)

# Core price arrays
o = np.array(open)
h = np.array(high)
l = np.array(low)
c = np.array(close)
n = len(c)

body = c - o
abs_body = np.abs(body)
upper_wick = h - np.maximum(o, c)
lower_wick = np.minimum(o, c) - l
full_range = h - l
avg_body = np.full(n, np.nan)

for i in range(20, n):
    avg_body[i] = np.mean(abs_body[i - 20:i])

avg_body = np.nan_to_num(avg_body, nan=1e-10)
small_body = abs_body < avg_body * 0.3
big_body = abs_body > avg_body * 0.7

# --- Pattern Detection (boolean arrays) ---

# Hammer: small upper wick, long lower wick, small-ish body at top
hammer = (
    (lower_wick > abs_body * 2)
    & (upper_wick < abs_body * 0.5)
    & (full_range > 0)
)

# Inverted Hammer
inv_hammer = (
    (upper_wick > abs_body * 2)
    & (lower_wick < abs_body * 0.5)
    & (full_range > 0)
)

# Doji: very small body relative to range
doji = (
    small_body
    & (full_range > 0)
    & (abs_body < full_range * 0.1)
)

# Bullish Engulfing: prev red, current green, current body engulfs prev body
bull_engulf = np.zeros(n, dtype=bool)
bull_engulf[1:] = (
    (body[:-1] < 0)
    & (body[1:] > 0)
    & (o[1:] <= c[:-1])
    & (c[1:] >= o[:-1])
    & big_body[1:]
)

# Bearish Engulfing
bear_engulf = np.zeros(n, dtype=bool)
bear_engulf[1:] = (
    (body[:-1] > 0)
    & (body[1:] < 0)
    & (o[1:] >= c[:-1])
    & (c[1:] <= o[:-1])
    & big_body[1:]
)

# Bullish Harami: prev big red, current small green inside prev body
bull_harami = np.zeros(n, dtype=bool)
bull_harami[1:] = (
    (body[:-1] < 0)
    & (body[1:] > 0)
    & small_body[1:]
    & big_body[:-1]
    & (o[1:] >= c[:-1])
    & (c[1:] <= o[:-1])
)

# Bearish Harami
bear_harami = np.zeros(n, dtype=bool)
bear_harami[1:] = (
    (body[:-1] > 0)
    & (body[1:] < 0)
    & small_body[1:]
    & big_body[:-1]
    & (o[1:] <= c[:-1])
    & (c[1:] >= o[:-1])
)

# Morning Star (3-bar): big red, small body gap down, big green
morning_star = np.zeros(n, dtype=bool)
morning_star[2:] = (
    (body[:-2] < 0)
    & big_body[:-2]
    & small_body[1:-1]
    & (body[2:] > 0)
    & big_body[2:]
    & (c[2:] > (o[:-2] + c[:-2]) / 2)
)

# Evening Star (3-bar): big green, small body gap up, big red
evening_star = np.zeros(n, dtype=bool)
evening_star[2:] = (
    (body[:-2] > 0)
    & big_body[:-2]
    & small_body[1:-1]
    & (body[2:] < 0)
    & big_body[2:]
    & (c[2:] < (o[:-2] + c[:-2]) / 2)
)

# --- Success Rate Calculation ---
# For bullish patterns, success = close rose within 5 bars
# For bearish patterns, success = close fell within 5 bars
horizon = 5


def calc_hit_rate(pattern_mask, bullish):
    """Calculate rolling hit rate for a pattern over the lookback window."""
    rate = np.zeros(n)
    for i in range(lookback, n):
        window = pattern_mask[i - lookback:i]
        indices = np.where(window)[0] + (i - lookback)
        if len(indices) == 0:
            rate[i] = 0.5
            continue
        hits = 0
        total = 0
        for idx in indices:
            if idx + horizon < n:
                total += 1
                if bullish and c[idx + horizon] > c[idx]:
                    hits += 1
                elif (not bullish) and c[idx + horizon] < c[idx]:
                    hits += 1
        rate[i] = hits / total if total > 0 else 0.5
    return rate


# Bullish patterns: direction = +1
# Bearish patterns: direction = -1
patterns = [
    (hammer,       True,  "Hammer"),
    (inv_hammer,   True,  "Inv Hammer"),
    (doji,         True,  "Doji"),
    (bull_engulf,  True,  "Bull Engulf"),
    (bear_engulf,  False, "Bear Engulf"),
    (bull_harami,  True,  "Bull Harami"),
    (bear_harami,  False, "Bear Harami"),
    (morning_star, True,  "Morning Star"),
    (evening_star, False, "Evening Star"),
]

composite = np.zeros(n)

for mask, bullish, name in patterns:
    hr = calc_hit_rate(mask, bullish)
    direction = 1.0 if bullish else -1.0
    composite += mask.astype(float) * direction * hr

# Scale to -100..+100 range
max_abs = np.max(np.abs(composite))
if max_abs > 0:
    composite = composite / max_abs * 100.0

plot(composite, title="Pattern Score", color="#26C6DA")
hline(0, title="Zero", color="#888888")
hline(50, title="Strong Bull", color="rgba(76,175,80,0.3)")
hline(-50, title="Strong Bear", color="rgba(244,67,54,0.3)")

bgcolor(composite > 50, color="rgba(76,175,80,0.15)")
bgcolor(composite < -50, color="rgba(244,67,54,0.15)")
