from tg_scripting import *

length = input.int(50, "Lookback Length", minval=20, maxval=200)
num_levels = input.int(10, "Number of Levels", minval=5, maxval=20)

import numpy as np

hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo
step = rng / num_levels

mid_price = (hi + lo) / 2
vol_at_mid = ta.sma(volume, length)
vol_above = ta.sma(volume * (close > mid_price), length)
vol_below = ta.sma(volume * (close < mid_price), length)

vol_ratio = vol_above / (vol_above + vol_below + 1e-10) * 100

plot(vol_ratio, title="Volume Above/Below Ratio", color="#42A5F5")
plot(ta.sma(vol_ratio, 5), title="Smoothed Ratio", color="#FF7043")
hline(50, title="Equal Distribution", color="rgba(128,128,128,0.4)")
hline(70, title="Volume Skew Up", color="rgba(38,166,154,0.5)")
hline(30, title="Volume Skew Down", color="rgba(239,83,80,0.5)")

plot(mid_price, title="Mid Price", color="#AB47BC")
plot(hi, title="Range High", color="rgba(239,83,80,0.4)")
plot(lo, title="Range Low", color="rgba(38,166,154,0.4)")

bgcolor(vol_ratio > 70, color="rgba(38,166,154,0.06)")
bgcolor(vol_ratio < 30, color="rgba(239,83,80,0.06)")
