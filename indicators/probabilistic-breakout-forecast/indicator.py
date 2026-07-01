from tg_scripting import *
import numpy as np

range_len = input.int(20, "Range Length", minval=5, maxval=100)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
prob_threshold = input.float(80.0, "Probability Threshold")

range_high = ta.highest(high, range_len)
range_low = ta.lowest(low, range_len)

c = np.array(close, dtype=float)
rh = np.array(range_high, dtype=float)
rl = np.array(range_low, dtype=float)

range_width = (rh - rl) / c * 100.0

atr_val = ta.atr(high, low, close, atr_len)
atr_pct = np.array(atr_val, dtype=float) / c * 100.0

compression = range_width / (atr_pct * np.sqrt(range_len) + 0.001)

h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
n = len(c)
bars_in = np.zeros(n)
for i in range(1, n):
    if h[i] < rh[i] and l[i] > rl[i]:
        bars_in[i] = bars_in[i - 1] + 1.0

time_factor = bars_in / range_len
compression_factor = 1.0 / (compression + 0.01)

probability = np.clip((1.0 - np.exp(-compression_factor * time_factor)) * 100.0, 0.0, 100.0)

high_prob = probability >= prob_threshold
elevated = probability >= 70.0

plot(probability, title="Breakout Probability", color="#00bcd4")
hline(prob_threshold, title="Threshold", color="#ff9800")
hline(50.0, title="Midline", color="#555555")
plotshape(high_prob, title="High Probability", style="triangleup", location="belowbar", color="#00e676")
bgcolor(elevated, color="rgba(0, 188, 212, 0.08)")
