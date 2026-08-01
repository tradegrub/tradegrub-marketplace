from tg_scripting import *
import numpy as np

indicator("Pin Bar Detector", overlay=True)

wick_ratio = input.float(2.5, "Min Wick to Body Ratio", minval=1.5, maxval=5.0, step=0.1)
small_wick_pct = input.float(0.2, "Max Small Wick %", minval=0.05, maxval=0.5, step=0.05)
min_range_atr = input.float(0.8, "Min Range vs ATR", minval=0.3, maxval=2.0, step=0.1)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
trend_len = input.int(20, "Trend MA Length", minval=5, maxval=100)

o = np.array(open, dtype=float)
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

atr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
trend_ma = np.array(ta.sma(close, trend_len), dtype=float)

body = np.abs(c - o)
rng = h - l
rng = np.where(rng == 0, 0.0001, rng)
upper_wick = h - np.maximum(c, o)
lower_wick = np.minimum(c, o) - l

bull_pin = np.zeros(n, dtype=bool)
bear_pin = np.zeros(n, dtype=bool)

for i in range(1, n):
    if body[i] < 0.0001:
        continue
    if rng[i] < atr[i] * min_range_atr:
        continue

    # Bullish pin bar: long lower wick, small upper wick
    if (lower_wick[i] > body[i] * wick_ratio and
        upper_wick[i] < rng[i] * small_wick_pct and
        c[i] < trend_ma[i]):
        bull_pin[i] = True

    # Bearish pin bar: long upper wick, small lower wick
    if (upper_wick[i] > body[i] * wick_ratio and
        lower_wick[i] < rng[i] * small_wick_pct and
        c[i] > trend_ma[i]):
        bear_pin[i] = True

# Strength score based on wick length relative to ATR
strength = np.zeros(n)
for i in range(n):
    if bull_pin[i]:
        strength[i] = lower_wick[i] / atr[i] if atr[i] > 0 else 0
    elif bear_pin[i]:
        strength[i] = -(upper_wick[i] / atr[i]) if atr[i] > 0 else 0

plotshape(bull_pin, title="Bullish Pin Bar", style="triangleup", location="belowbar", color="#00e676")
plotshape(bear_pin, title="Bearish Pin Bar", style="triangledown", location="abovebar", color="#FF5252")
plot(strength.tolist(), title="Pin Strength", color="#42A5F5", linewidth=1)
plot(trend_ma.tolist(), title="Trend MA", color="#FFD54F", linewidth=1)
