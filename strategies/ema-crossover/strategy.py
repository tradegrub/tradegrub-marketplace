# EMA Crossover Strategy
from tg_scripting import *

fast_len = input.int(9, "Fast EMA Length", minval=2, maxval=50)
slow_len = input.int(21, "Slow EMA Length", minval=5, maxval=200)
trend_len = input.int(100, "Trend Filter EMA", minval=20, maxval=500)

fast_ema = ta.ema(close, fast_len)
slow_ema = ta.ema(close, slow_len)
trend_ema = ta.ema(close, trend_len)

long_cond = ta.crossover(fast_ema, slow_ema)[-1] and close[-1] > trend_ema[-1]
exit_cond = ta.crossunder(fast_ema, slow_ema)[-1]

if long_cond:
    strategy.entry("Long", strategy.LONG)
if exit_cond:
    strategy.close("Long")

p1 = plot(fast_ema, title="Fast EMA", color="orange")
p2 = plot(slow_ema, title="Slow EMA", color="blue")
plot(trend_ema, title="Trend Filter", color="gray")
fill(p1, p2, color="rgba(0,150,255,0.1)")
