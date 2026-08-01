from tg_scripting import *
import numpy as np

smooth_length = input.int(10, "Smoothing Length", minval=2, maxval=50)

# Compute wick sizes
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
o = np.array(open, dtype=float)
c = np.array(close, dtype=float)

upper_wick = h - np.maximum(o, c)
lower_wick = np.minimum(o, c) - l

# Wick Asymmetry Ratio: positive = more lower wicks (buying pressure)
war = (lower_wick - upper_wick) / (upper_wick + lower_wick + 0.001)

# Smooth with EMA
smoothed = ta.ema(war, smooth_length)

plot(smoothed, title="Wick Asymmetry", color="#00BBFF")
hline(0.0, title="Zero Line", color="#666666")
hline(0.5, title="Strong Buying", color="#00AA55")
hline(-0.5, title="Strong Selling", color="#FF4444")

# Color background for extreme readings
bgcolor(smoothed > 0.5, color="rgba(0,170,85,0.1)")
bgcolor(smoothed < -0.5, color="rgba(255,68,68,0.1)")
