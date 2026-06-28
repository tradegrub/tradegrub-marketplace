# Triple Moving Average Strategy
from tg_scripting import *

fast_len = input.int(10, "Fast SMA", minval=2, maxval=50)
mid_len = input.int(20, "Mid SMA", minval=5, maxval=100)
slow_len = input.int(50, "Slow SMA", minval=20, maxval=200)

fast_sma = ta.sma(close, fast_len)
mid_sma = ta.sma(close, mid_len)
slow_sma = ta.sma(close, slow_len)

long_cond = ta.crossover(fast_sma, mid_sma)[-1] and mid_sma[-1] > slow_sma[-1]
exit_cond = ta.crossunder(fast_sma, mid_sma)[-1]

if long_cond:
    strategy.entry("Long", strategy.LONG)
if exit_cond:
    strategy.close("Long")

p1 = plot(fast_sma, title="Fast SMA", color="lime")
p2 = plot(mid_sma, title="Mid SMA", color="orange")
p3 = plot(slow_sma, title="Slow SMA", color="red")
fill(p1, p2, color="rgba(0,255,0,0.08)")
