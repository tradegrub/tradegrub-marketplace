# Ichimoku Cloud Strategy
from tg_scripting import *

tenkan_len = input.int(9, "Tenkan Period", minval=2, maxval=50)
kijun_len = input.int(26, "Kijun Period", minval=5, maxval=100)
senkou_b_len = input.int(52, "Senkou B Period", minval=10, maxval=200)

tenkan, kijun, senkou_a, senkou_b, chikou = ta.ichimoku(high, low, close, tenkan_len, kijun_len, senkou_b_len)

cloud_top = np.maximum(senkou_a, senkou_b)
above_cloud = close[-1] > cloud_top[-1]
tk_cross = ta.crossover(tenkan, kijun)[-1]

long_cond = above_cloud and tk_cross
exit_cond = ta.crossunder(tenkan, kijun)[-1]

if long_cond:
    strategy.entry("Long", strategy.LONG)
if exit_cond:
    strategy.close("Long")

plot(tenkan, title="Tenkan-sen", color="blue")
plot(kijun, title="Kijun-sen", color="red")
p1 = plot(senkou_a, title="Senkou A", color="green")
p2 = plot(senkou_b, title="Senkou B", color="maroon")
fill(p1, p2, color="rgba(0,128,0,0.1)")
