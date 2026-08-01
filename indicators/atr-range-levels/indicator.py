from tg_scripting import *
import numpy as np

indicator("ATR Range Levels", overlay=True)

atr_len = input.int(14, "ATR Length", minval=2, maxval=100)
multiplier = input.float(1.0, "Multiplier", minval=0.1, maxval=5.0, step=0.1)
show_half = input.bool(True, "Show 50% Levels")

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

# Calculate ATR
tr = np.zeros(n)
tr[0] = hi[0] - lo[0]
for i in range(1, n):
    tr[i] = max(hi[i] - lo[i], abs(hi[i] - cl[i-1]), abs(lo[i] - cl[i-1]))

atr = np.zeros(n)
if n >= atr_len:
    atr[atr_len-1] = np.mean(tr[:atr_len])
    alpha = 1.0 / atr_len
    for i in range(atr_len, n):
        atr[i] = atr[i-1] * (1 - alpha) + tr[i] * alpha

# Reference price: first bar's close as daily anchor
# Use SMA of close as a smoothed anchor to reduce noise
sma_anchor = np.zeros(n)
for i in range(atr_len, n):
    sma_anchor[i] = np.mean(cl[i-atr_len:i+1])
# For bars before enough data, use close
sma_anchor[:atr_len] = cl[:atr_len]

ref = sma_anchor

# Range levels
upper = ref + atr * multiplier
lower = ref - atr * multiplier
half_upper = ref + atr * multiplier * 0.5
half_lower = ref - atr * multiplier * 0.5

# Only plot from atr_len onward where values are valid
valid_start = atr_len

upper_list = upper[valid_start:].tolist()
lower_list = lower[valid_start:].tolist()
ref_list = ref[valid_start:].tolist()

p_upper = plot(upper_list, title="Upper Range", color="#f44336", linewidth=2)
p_lower = plot(lower_list, title="Lower Range", color="#4CAF50", linewidth=2)
p_ref = plot(ref_list, title="Reference", color="#42a5f5", linewidth=1)

fill(p_upper, p_lower, color="rgba(33,150,243,0.06)")

if show_half:
    half_upper_list = half_upper[valid_start:].tolist()
    half_lower_list = half_lower[valid_start:].tolist()
    plot(half_upper_list, title="50% Upper", color="#FF9800", linewidth=1)
    plot(half_lower_list, title="50% Lower", color="#FF9800", linewidth=1)

# Color-coded background zones
near_upper = np.zeros(n, dtype=bool)
near_lower = np.zeros(n, dtype=bool)
near_half = np.zeros(n, dtype=bool)

for i in range(valid_start, n):
    range_size = atr[i] * multiplier
    if range_size > 0:
        dist = abs(cl[i] - ref[i]) / range_size
        if dist >= 0.8:
            near_upper[i] = True
        elif dist >= 0.4:
            near_half[i] = True

bgcolor(near_upper[valid_start:].tolist(), color="rgba(244,67,54,0.08)")
bgcolor(near_half[valid_start:].tolist(), color="rgba(255,152,0,0.06)")

# End labels
if n > valid_start + 5:
    label.new(x=n-1, y=float(upper[n-1]),
              text=f"ATR Hi: {upper[n-1]:.2f}",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#f44336", size="small")
    label.new(x=n-1, y=float(lower[n-1]),
              text=f"ATR Lo: {lower[n-1]:.2f}",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#4CAF50", size="small")
