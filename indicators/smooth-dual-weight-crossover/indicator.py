from tg_scripting import *
import numpy as np

indicator("Smooth Dual-Weight Crossover", overlay=True)

fast_len = input.int(8, "Fast Length", minval=3, maxval=30)
slow_len = input.int(21, "Slow Length", minval=10, maxval=100)
phase_adj = input.float(0.5, "Phase Adjustment", minval=0.0, maxval=1.0, step=0.1)

src = np.array(close, dtype=float)
n = len(src)

def smooth_ma(data, length, phase):
    out = np.copy(data)
    beta = phase / (length + 1)
    alpha = 2.0 / (length + 1)
    for i in range(1, len(data)):
        out[i] = (alpha + beta) * data[i] + (1 - alpha) * out[i-1] - beta * out[max(0, i-1)]
    stage2 = np.copy(out)
    for i in range(1, len(data)):
        stage2[i] = alpha * out[i] + (1 - alpha) * stage2[i-1]
    return stage2

fast = smooth_ma(src, fast_len, phase_adj)
slow = smooth_ma(src, slow_len, phase_adj)

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if fast[i] > slow[i] and fast[i-1] <= slow[i-1]:
        cross_up[i] = True
    elif fast[i] < slow[i] and fast[i-1] >= slow[i-1]:
        cross_down[i] = True


plot(fast.tolist(), title="Fast Smooth", color="#26c6da", linewidth=2)
plot(slow.tolist(), title="Slow Smooth", color="#ef5350", linewidth=2)
plotshape(cross_up.tolist(), title="Cross Up", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Cross Down", style="triangledown", location="abovebar", color="#ff1744", size="small")
