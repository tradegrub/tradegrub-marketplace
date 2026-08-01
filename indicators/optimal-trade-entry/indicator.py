from tg_scripting import *
import numpy as np

indicator("Optimal Trade Entry Zone", overlay=True)

swing_len = input.int(10, "Swing Lookback", minval=3, maxval=50)
fib_upper = input.float(0.618, "Upper Fib Level", minval=0.5, maxval=0.9, step=0.01)
fib_lower = input.float(0.786, "Lower Fib Level", minval=0.6, maxval=1.0, step=0.01)
show_zone = input.bool(True, "Show OTE Zone")
show_fibs = input.bool(True, "Show Fib Levels")

n = len(close)
atr = ta.atr(high, low, close, 14)

# Find swing highs and lows
swing_hi_idx = []
swing_lo_idx = []
for i in range(swing_len, n - swing_len):
    if high[i] == max(high[max(0, i - swing_len):i + swing_len + 1]):
        swing_hi_idx.append(i)
    if low[i] == min(low[max(0, i - swing_len):i + swing_len + 1]):
        swing_lo_idx.append(i)

ote_top = np.full(n, np.nan)
ote_bot = np.full(n, np.nan)
fib_50 = np.full(n, np.nan)
in_bull_ote = np.zeros(n, dtype=bool)
in_bear_ote = np.zeros(n, dtype=bool)

# Project OTE zones from most recent swing pairs
last_label = -20
for i in range(swing_len * 2, n):
    # Find most recent swing low and swing high before i
    recent_hi = None
    recent_lo = None
    for idx in reversed(swing_hi_idx):
        if idx < i:
            recent_hi = idx
            break
    for idx in reversed(swing_lo_idx):
        if idx < i:
            recent_lo = idx
            break

    if recent_hi is None or recent_lo is None:
        continue

    hi_val = float(high[recent_hi])
    lo_val = float(low[recent_lo])
    rng = hi_val - lo_val
    if rng <= 0:
        continue

    if recent_lo < recent_hi:
        # Bullish swing: low then high, OTE is pullback zone
        top = hi_val - rng * fib_upper
        bot = hi_val - rng * fib_lower
        mid = hi_val - rng * 0.5
        ote_top[i] = top
        ote_bot[i] = bot
        fib_50[i] = mid
        if float(low[i]) <= top and float(close[i]) >= bot:
            in_bull_ote[i] = True
    else:
        # Bearish swing: high then low, OTE is pullback zone
        top = lo_val + rng * fib_lower
        bot = lo_val + rng * fib_upper
        mid = lo_val + rng * 0.5
        ote_top[i] = top
        ote_bot[i] = bot
        fib_50[i] = mid
        if float(high[i]) >= bot and float(close[i]) <= top:
            in_bear_ote[i] = True

if show_zone:
    plot(ote_top, title="OTE Upper", color="rgba(66,165,245,0.6)", linewidth=1)
    plot(ote_bot, title="OTE Lower", color="rgba(66,165,245,0.6)", linewidth=1)

if show_fibs:
    plot(fib_50, title="50% Fib", color="rgba(255,255,255,0.3)", linewidth=1, style="dashed")

bgcolor(in_bull_ote, color="rgba(0,230,118,0.06)")
bgcolor(in_bear_ote, color="rgba(255,23,68,0.06)")

plotshape(in_bull_ote, title="Bull OTE", shape="triangleup", location="belowbar", color="#00e676", size="tiny")
plotshape(in_bear_ote, title="Bear OTE", shape="triangledown", location="abovebar", color="#ff1744", size="tiny")
