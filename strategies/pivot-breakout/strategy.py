# Pivot Point Breakout Strategy
from tg_scripting import *

lookback = input.int(5, "Pivot Lookback", minval=2, maxval=20)
confirm_bars = input.int(2, "Confirmation Bars", minval=1, maxval=5)
use_volume = input.bool(True, "Require Volume Confirmation")
vol_mult = input.float(1.5, "Volume Multiplier", minval=1.0, maxval=3.0)

# Find pivot highs and lows using highest/lowest
pivot_high = ta.highest(high, lookback)
pivot_low = ta.lowest(low, lookback)

# Volume filter
avg_vol = ta.sma(volume, 20)
vol_confirm = volume > avg_vol * vol_mult if use_volume else np.ones(len(close), dtype=bool)

# Breakout above pivot high
long_signal = (close > pivot_high) & vol_confirm
short_signal = (close < pivot_low) & vol_confirm

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when price returns to mid range
mid = (pivot_high + pivot_low) / 2
if ta.crossunder(close, mid)[-1]:
    strategy.close("Long")

if ta.crossover(close, mid)[-1]:
    strategy.close("Short")

p1 = plot(pivot_high, title="Pivot High", color="green")
p2 = plot(pivot_low, title="Pivot Low", color="red")
plot(mid, title="Mid Line", color="orange")
fill(p1, p2, color="rgba(100, 100, 200, 0.06)")

plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")
