from tg_scripting import *
import numpy as np

pivot_len = input.int(5, "Pivot Length", minval=2, maxval=50)
lookback = input.int(50, "Lookback Period", minval=10, maxval=200)

h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)

pivot_window = pivot_len * 2 + 1
highest_vals = ta.highest(high, pivot_window)
lowest_vals = ta.lowest(low, pivot_window)

is_sh = (h == np.array(highest_vals, dtype=float))
is_sl = (l == np.array(lowest_vals, dtype=float))

swing_high_level = np.nan
swing_low_level = np.nan

for i in range(pivot_len, min(lookback, len(h))):
    if is_sh[i]:
        swing_high_level = h[i]
        break

for i in range(pivot_len, min(lookback, len(l))):
    if is_sl[i]:
        swing_low_level = l[i]
        break

cur_h = h[0]
cur_l = l[0]
cur_c = c[0]

bearish_sfp = False
bullish_sfp = False

if not np.isnan(swing_high_level) and cur_h > swing_high_level and cur_c < swing_high_level:
    bearish_sfp = True

if not np.isnan(swing_low_level) and cur_l < swing_low_level and cur_c > swing_low_level:
    bullish_sfp = True

if bearish_sfp:
    plotshape(True, title="Bearish SFP", style="triangledown", location="abovebar", color="#ef5350")
    hline(swing_high_level, title="Swept High", color="#ef5350")

if bullish_sfp:
    plotshape(True, title="Bullish SFP", style="triangleup", location="belowbar", color="#26a69a")
    hline(swing_low_level, title="Swept Low", color="#26a69a")

sfp_val = 0
if bullish_sfp:
    sfp_val = 1
if bearish_sfp:
    sfp_val = -1

plot(sfp_val, title="SFP Signal", color="#ffffff")
