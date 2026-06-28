# Bollinger/Keltner Squeeze Momentum Strategy
from tg_scripting import *

bb_length = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0)
kc_length = input.int(20, "KC Length", minval=5, maxval=50)
kc_mult = input.float(1.5, "KC Multiplier", minval=0.5, maxval=4.0)

squeeze_on, momentum = ta.squeeze(close, high, low, close, bb_length, bb_mult, kc_length, kc_mult)

# Enter long when squeeze fires (was on, now off) and momentum is positive
squeeze_off = squeeze_on[-2] and not squeeze_on[-1]

if squeeze_off and momentum[-1] > 0:
    strategy.entry("Long", strategy.LONG)

# Exit when momentum turns negative
if momentum[-1] < 0 and momentum[-2] >= 0:
    strategy.close("Long")

plot(momentum, title="Momentum", color="teal")
bgcolor(squeeze_on[-1], color="rgba(255,0,0,0.1)")
hline(0, title="Zero", color="gray")
