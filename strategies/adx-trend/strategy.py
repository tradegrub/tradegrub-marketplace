# ADX Trend Strategy
from tg_scripting import *

di_len = input.int(14, "DI Length", minval=5, maxval=50)
adx_len = input.int(14, "ADX Smoothing", minval=5, maxval=50)
adx_thresh = input.float(25.0, "ADX Threshold", minval=15.0, maxval=50.0)

plus_di, minus_di, adx_val = ta.dmi(high, low, close, di_len)

strong_trend = adx_val[-1] > adx_thresh
di_cross_up = ta.crossover(plus_di, minus_di)[-1]
di_cross_down = ta.crossunder(plus_di, minus_di)[-1]

if di_cross_up and strong_trend:
    strategy.entry("Long", strategy.LONG)
if di_cross_down:
    strategy.close("Long")

plot(plus_di, title="+DI", color="green")
plot(minus_di, title="-DI", color="red")
plot(adx_val, title="ADX", color="blue")
hline(adx_thresh, title="Threshold", color="gray")
