from tg_scripting import *
import numpy as np

indicator("Candlestick Pattern Scanner", overlay=True)

show_doji = input.bool(True, "Show Doji")
show_engulf = input.bool(True, "Show Engulfing")
show_hammer = input.bool(True, "Show Hammer/Hanging Man")
show_star = input.bool(True, "Show Shooting/Morning Star")
show_harami = input.bool(True, "Show Harami")
body_pct = input.float(0.1, "Doji Body Ratio", minval=0.01, maxval=0.3, step=0.01)

o = np.array(open, dtype=float)
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

body = np.abs(c - o)
rng = h - l
rng = np.where(rng == 0, 0.0001, rng)
body_ratio = body / rng
upper_wick = h - np.maximum(c, o)
lower_wick = np.minimum(c, o) - l
bullish = c > o
bearish = c < o

# Pattern arrays
bull_signals = np.zeros(n, dtype=bool)
bear_signals = np.zeros(n, dtype=bool)
pattern_val = np.zeros(n)

for i in range(2, n):
    # Doji
    if show_doji and body_ratio[i] < body_pct:
        if lower_wick[i] > body[i] * 2:
            bull_signals[i] = True
            pattern_val[i] = 1
        elif upper_wick[i] > body[i] * 2:
            bear_signals[i] = True
            pattern_val[i] = -1

    # Bullish Engulfing
    if show_engulf and bearish[i-1] and bullish[i]:
        if c[i] > o[i-1] and o[i] < c[i-1] and body[i] > body[i-1]:
            bull_signals[i] = True
            pattern_val[i] = 2

    # Bearish Engulfing
    if show_engulf and bullish[i-1] and bearish[i]:
        if c[i] < o[i-1] and o[i] > c[i-1] and body[i] > body[i-1]:
            bear_signals[i] = True
            pattern_val[i] = -2

    # Hammer (bullish)
    if show_hammer and lower_wick[i] > body[i] * 2 and upper_wick[i] < body[i] * 0.5:
        if bearish[i-1] and bearish[i-2]:
            bull_signals[i] = True
            pattern_val[i] = 3

    # Hanging Man (bearish)
    if show_hammer and lower_wick[i] > body[i] * 2 and upper_wick[i] < body[i] * 0.5:
        if bullish[i-1] and bullish[i-2]:
            bear_signals[i] = True
            pattern_val[i] = -3

    # Shooting Star
    if show_star and upper_wick[i] > body[i] * 2 and lower_wick[i] < body[i] * 0.5:
        if bullish[i-1]:
            bear_signals[i] = True
            pattern_val[i] = -4

    # Inverted Hammer
    if show_star and upper_wick[i] > body[i] * 2 and lower_wick[i] < body[i] * 0.5:
        if bearish[i-1]:
            bull_signals[i] = True
            pattern_val[i] = 4

    # Bullish Harami
    if show_harami and bearish[i-1] and bullish[i]:
        if o[i] > c[i-1] and c[i] < o[i-1] and body[i] < body[i-1] * 0.5:
            bull_signals[i] = True
            pattern_val[i] = 5

    # Bearish Harami
    if show_harami and bullish[i-1] and bearish[i]:
        if o[i] < c[i-1] and c[i] > o[i-1] and body[i] < body[i-1] * 0.5:
            bear_signals[i] = True
            pattern_val[i] = -5

plotshape(bull_signals, title="Bullish Pattern", style="triangleup", location="belowbar", color="#00e676")
plotshape(bear_signals, title="Bearish Pattern", style="triangledown", location="abovebar", color="#FF5252")
plot(pattern_val.tolist(), title="Pattern ID", color="#42A5F5", linewidth=1)
