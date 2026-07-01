from tg_scripting import *
import numpy as np

indicator("WaveTrend Oscillator", overlay=False)

# Inputs
ch_len = input.int(9, "Channel Length", minval=1, maxval=50)
avg_len = input.int(12, "Average Length", minval=1, maxval=50)
ob_level = input.float(60.0, "Overbought", minval=20.0, maxval=100.0)
os_level = input.float(-60.0, "Oversold", minval=-100.0, maxval=-20.0)

# Calculate typical price
hlc3 = (np.array(high) + np.array(low) + np.array(close)) / 3.0

# EMA of typical price
esa = ta.ema(hlc3.tolist(), ch_len)

# Mean deviation
diff = np.abs(hlc3 - np.array(esa))
d = ta.ema(diff.tolist(), ch_len)

# Channel index
d_safe = np.where(np.array(d) == 0, 1.0, np.array(d))
ci = (hlc3 - np.array(esa)) / (0.015 * d_safe)

# WaveTrend lines
wt1 = np.array(ta.ema(ci.tolist(), avg_len))
wt2 = np.array(ta.sma(wt1.tolist(), 4))

# Cross signals
cross_up = np.zeros(len(close), dtype=bool)
cross_down = np.zeros(len(close), dtype=bool)
for i in range(1, len(close)):
    if wt1[i] > wt2[i] and wt1[i - 1] <= wt2[i - 1]:
        cross_up[i] = True
    elif wt1[i] < wt2[i] and wt1[i - 1] >= wt2[i - 1]:
        cross_down[i] = True

# Overbought / oversold background
ob_zone = wt1 > ob_level
os_zone = wt1 < os_level

# Plots
plot(wt1.tolist(), title="WT1", color="#42A5F5", linewidth=2)
plot(wt2.tolist(), title="WT2", color="#FF7043", linewidth=1)
hline(ob_level, title="Overbought", color="#ef5350", linestyle="dashed")
hline(os_level, title="Oversold", color="#26a69a", linestyle="dashed")
hline(0.0, title="Zero", color="#555555", linestyle="dashed")
bgcolor(ob_zone, color="rgba(239,83,80,0.08)")
bgcolor(os_zone, color="rgba(38,166,154,0.08)")
plotshape(cross_up, title="Buy", style="triangleup", location="belowbar", color="#00e676")
plotshape(cross_down, title="Sell", style="triangledown", location="abovebar", color="#ff1744")
