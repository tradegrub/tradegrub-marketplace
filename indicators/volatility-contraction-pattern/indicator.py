from tg_scripting import *
import numpy as np

indicator("Volatility Contraction Pattern", overlay=True)

range_period = input.int(10, "Range Period", minval=3, maxval=50)
base_period = input.int(40, "Base Period", minval=20, maxval=200)
vol_period = input.int(20, "Volume Period", minval=5, maxval=100)
contraction_threshold = input.float(0.5, "Contraction Threshold")

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

# Range contraction: short range vs long range
short_high = np.array(ta.highest(high, range_period), dtype=float)
short_low = np.array(ta.lowest(low, range_period), dtype=float)
long_high = np.array(ta.highest(high, base_period), dtype=float)
long_low = np.array(ta.lowest(low, base_period), dtype=float)

short_range = short_high - short_low
long_range = long_high - long_low
long_range_safe = np.where(long_range == 0, 1, long_range)
range_ratio = short_range / long_range_safe

# ATR contraction
atr_short = np.array(ta.atr(high, low, close, range_period), dtype=float)
atr_long = np.array(ta.atr(high, low, close, base_period), dtype=float)
atr_long_safe = np.where(atr_long == 0, 1, atr_long)
atr_ratio = atr_short / atr_long_safe

# Volume contraction
vol_sma_short = np.array(ta.sma(volume, vol_period), dtype=float)
vol_sma_long = np.array(ta.sma(volume, base_period), dtype=float)
vol_sma_long_safe = np.where(vol_sma_long == 0, 1, vol_sma_long)
vol_ratio = vol_sma_short / vol_sma_long_safe

# VCP conditions
range_contracting = range_ratio < contraction_threshold
atr_contracting = atr_ratio < 0.7
vol_contracting = vol_ratio < 0.8

# VCP score: all three contracting simultaneously
vcp_active = range_contracting & atr_contracting & vol_contracting

# Breakout level: highest high over the range period
breakout_level = short_high.copy()
# Only show breakout level during VCP zones
breakout_display = np.where(vcp_active, breakout_level, np.nan)

# Background highlight for VCP zones
bgcolor(vcp_active.tolist(), color="rgba(0,229,255,0.08)")

# Plot breakout level
plot(breakout_display.tolist(), title="Breakout Level", color="#ff9800")

# Mark start of new VCP zones
vcp_start = np.full(n, False)
for i in range(1, n):
    if vcp_active[i] and not vcp_active[i - 1]:
        vcp_start[i] = True

plotshape(vcp_start.tolist(), title="VCP Start", style="triangleup", location="belowbar", color="#00e676")
