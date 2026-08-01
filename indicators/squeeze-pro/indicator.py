from tg_scripting import *
import numpy as np

indicator("Squeeze Pro", overlay=False)

bb_len = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0, step=0.1)
kc_len = input.int(20, "KC Length", minval=5, maxval=50)
kc_mult1 = input.float(1.5, "KC Mult Low", minval=0.5, maxval=3.0, step=0.1)
kc_mult2 = input.float(2.0, "KC Mult Mid", minval=1.0, maxval=4.0, step=0.1)
kc_mult3 = input.float(3.0, "KC Mult High", minval=1.5, maxval=5.0, step=0.1)

src = np.array(close)
h = np.array(high)
l = np.array(low)
c = np.array(close)

# Bollinger Bands
bb_upper, bb_mid, bb_lower = ta.bb(close, bb_len, bb_mult)
bb_upper = np.array(bb_upper)
bb_lower = np.array(bb_lower)

# Keltner Channels (EMA +/- mult * ATR)
kc_ma = np.array(ta.ema(close, kc_len))
atr_val = np.array(ta.atr(high, low, close, kc_len))

kc_upper1 = kc_ma + kc_mult1 * atr_val
kc_lower1 = kc_ma - kc_mult1 * atr_val
kc_upper2 = kc_ma + kc_mult2 * atr_val
kc_lower2 = kc_ma - kc_mult2 * atr_val
kc_upper3 = kc_ma + kc_mult3 * atr_val
kc_lower3 = kc_ma - kc_mult3 * atr_val

# Squeeze states
squeeze_off = (bb_lower < kc_lower1) | (bb_upper > kc_upper1)
squeeze_low = ~squeeze_off & ((bb_lower >= kc_lower1) & (bb_upper <= kc_upper1))
squeeze_mid = (bb_lower >= kc_lower2) & (bb_upper <= kc_upper2)
squeeze_high = (bb_lower >= kc_lower3) & (bb_upper <= kc_upper3)

# Momentum (linear regression of close - midline of highest/lowest + EMA)
highest_h = np.array(ta.highest(high, kc_len))
lowest_l = np.array(ta.lowest(low, kc_len))
mid_hl = (highest_h + lowest_l) / 2.0
mid_val = (mid_hl + kc_ma) / 2.0
momentum = src - mid_val

# Color momentum bars
n = len(close)
mom_colors = []
for i in range(n):
    m = momentum[i]
    if i == 0:
        prev = 0
    else:
        prev = momentum[i - 1]
    if m >= 0:
        mom_colors.append("#00e676" if m > prev else "#1b5e20")
    else:
        mom_colors.append("#ff1744" if m < prev else "#b71c1c")

# Squeeze dots color
dot_colors = []
for i in range(n):
    if squeeze_high[i]:
        dot_colors.append("#ff6f00")
    elif squeeze_mid[i]:
        dot_colors.append("#ff1744")
    elif squeeze_low[i]:
        dot_colors.append("#000000")
    else:
        dot_colors.append("#00e676")

# Plot momentum histogram
plot(momentum.tolist(), title="Momentum", color="#42A5F5", linewidth=4)

# Squeeze indicator as zero-line dots
squeeze_on = squeeze_low | squeeze_mid | squeeze_high
zeros = [0.0] * n
plot(zeros, title="Squeeze", color="#888888", linewidth=3)

hline(0.0, title="Zero", color="#333333", linestyle="dashed")
