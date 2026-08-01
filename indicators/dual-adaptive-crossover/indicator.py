from tg_scripting import *
import numpy as np

indicator("Dual Adaptive Crossover", overlay=True)

fast_base = input.int(8, "Fast Base Period", minval=3, maxval=20)
slow_base = input.int(21, "Slow Base Period", minval=10, maxval=60)
adapt_len = input.int(20, "Adaptation Length", minval=10, maxval=50)

cl = np.array(close, dtype=float)
n = len(cl)

def adaptive_ma(data, base_period, adapt_length):
    out = np.copy(data)
    for i in range(1, len(data)):
        if i >= adapt_length:
            mom = abs(data[i] - data[max(0, i - adapt_length)])
            vol = sum(abs(data[j] - data[j-1]) for j in range(max(1, i - adapt_length + 1), i + 1))
            er = mom / max(vol, 1e-10)
        else:
            er = 0.5
        fast_sc = 2.0 / (base_period / 2 + 1)
        slow_sc = 2.0 / (base_period * 2 + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        out[i] = sc * data[i] + (1 - sc) * out[i-1]
    return out

fast_ma = adaptive_ma(cl, fast_base, adapt_len)
slow_ma = adaptive_ma(cl, slow_base, adapt_len)

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if fast_ma[i] > slow_ma[i] and fast_ma[i-1] <= slow_ma[i-1]:
        cross_up[i] = True
    elif fast_ma[i] < slow_ma[i] and fast_ma[i-1] >= slow_ma[i-1]:
        cross_down[i] = True


plot(fast_ma.tolist(), title="Fast Adaptive", color="#26c6da", linewidth=2)
plot(slow_ma.tolist(), title="Slow Adaptive", color="#ef5350", linewidth=2)
plotshape(cross_up.tolist(), title="Cross Up", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Cross Down", style="triangledown", location="abovebar", color="#ff1744", size="small")
