from tg_scripting import *
import numpy as np

lookback = input.int(20, "Lookback Period", minval=5, maxval=100)

# Get data as numpy arrays
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
o = np.array(open, dtype=float)
v = np.array(volume, dtype=float)

# Compute ATR manually with numpy
tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
tr[0] = h[0] - l[0]  # First bar has no previous close

# Rolling average ATR
avg_atr = np.full(len(c), np.nan)
for i in range(lookback, len(c)):
    avg_atr[i] = np.mean(tr[i - lookback:i])

# Volume ratio: current volume / average volume
avg_vol = np.full(len(c), np.nan)
for i in range(lookback, len(c)):
    avg_vol[i] = np.mean(v[i - lookback:i])

vol_ratio = np.where(avg_vol > 0, v / avg_vol, 1.0)

# Expected movement = volume_ratio * avg_atr
expected = vol_ratio * avg_atr

# Actual movement
actual = np.abs(c - o)

# Slippage = (expected - actual) / expected * 100
# High slippage = volume came in but price didn't move (absorption)
slippage = np.where(expected > 0, (expected - actual) / expected * 100.0, 0.0)

# Smooth with SMA
smoothed = ta.sma(slippage, lookback)

plot(smoothed, title="Kinetic Slippage", color="#FF55AA")
hline(50.0, title="High Slippage", color="#FF4444")
hline(0.0, title="Zero", color="#666666")

bgcolor(smoothed > 50, color="rgba(255,68,68,0.1)")
