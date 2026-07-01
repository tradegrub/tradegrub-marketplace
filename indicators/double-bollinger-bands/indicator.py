from tg_scripting import *
import numpy as np

indicator("Double Bollinger Bands", overlay=True)

bb_len = input.int(20, "BB Length", minval=5, maxval=200)
inner_mult = input.float(1.0, "Inner Multiplier", minval=0.1, maxval=5.0, step=0.1)
outer_mult = input.float(2.0, "Outer Multiplier", minval=0.1, maxval=5.0, step=0.1)

src = np.array(close, dtype=float)
n = len(src)

# Calculate SMA and standard deviation
sma = np.full(n, np.nan)
stdev = np.full(n, np.nan)
for i in range(bb_len - 1, n):
    window = src[i - bb_len + 1:i + 1]
    sma[i] = np.mean(window)
    stdev[i] = np.std(window, ddof=0)

# Inner bands (1 sigma by default)
inner_upper = sma + inner_mult * stdev
inner_lower = sma - inner_mult * stdev

# Outer bands (2 sigma by default)
outer_upper = sma + outer_mult * stdev
outer_lower = sma - outer_mult * stdev

# Plot center line
p_sma = plot(sma.tolist(), title="SMA", color="#FFFFFF", linewidth=2)

# Plot inner bands
p_inner_upper = plot(inner_upper.tolist(), title="Inner Upper", color="#42A5F5", linewidth=1)
p_inner_lower = plot(inner_lower.tolist(), title="Inner Lower", color="#42A5F5", linewidth=1)

# Plot outer bands
p_outer_upper = plot(outer_upper.tolist(), title="Outer Upper", color="#EF5350", linewidth=1)
p_outer_lower = plot(outer_lower.tolist(), title="Outer Lower", color="#EF5350", linewidth=1)

# Fill inner band area (normal zone) with subtle blue
fill(p_inner_upper, p_inner_lower, color="rgba(66,165,245,0.12)")

# Fill trending zones (between inner and outer bands) with subtle orange
fill(p_outer_upper, p_inner_upper, color="rgba(255,152,0,0.10)")
fill(p_inner_lower, p_outer_lower, color="rgba(255,152,0,0.10)")
