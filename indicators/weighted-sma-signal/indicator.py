from tg_scripting import *
import numpy as np

indicator("Weighted SMA Signal", overlay=True)

fast_len = input.int(10, "Fast Length", minval=3, maxval=30)
slow_len = input.int(30, "Slow Length", minval=15, maxval=100)

cl = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

def vwma(data, vol_data, length):
    out = np.zeros(n)
    for i in range(length, n):
        w = vol_data[i-length+1:i+1]
        v = data[i-length+1:i+1]
        total_w = np.sum(w)
        if total_w > 0:
            out[i] = np.sum(v * w) / total_w
        else:
            out[i] = np.mean(v)
    return out

fast_vwma = vwma(cl, vol, fast_len)
slow_vwma = vwma(cl, vol, slow_len)

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if fast_vwma[i] > slow_vwma[i] and fast_vwma[i-1] <= slow_vwma[i-1]:
        cross_up[i] = True
    elif fast_vwma[i] < slow_vwma[i] and fast_vwma[i-1] >= slow_vwma[i-1]:
        cross_down[i] = True


plot(fast_vwma.tolist(), title="Fast VWMA", color="#26c6da", linewidth=2)
plot(slow_vwma.tolist(), title="Slow VWMA", color="#ef5350", linewidth=2)
plotshape(cross_up.tolist(), title="Cross Up", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Cross Down", style="triangledown", location="abovebar", color="#ff1744", size="small")
