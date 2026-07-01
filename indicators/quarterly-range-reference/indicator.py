from tg_scripting import *
import numpy as np

indicator("Quarterly Range Reference", overlay=True)

period = input.int(63, "Quarterly Period", minval=40, maxval=80)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

q_hi = np.zeros(n)
q_lo = np.zeros(n)
q_open = np.zeros(n)

for i in range(period, n):
    q_hi[i] = np.max(hi[i-period:i+1])
    q_lo[i] = np.min(lo[i-period:i+1])
    q_open[i] = cl[i-period]

new_high = np.zeros(n, dtype=bool)
new_low = np.zeros(n, dtype=bool)
for i in range(period+1, n):
    if q_hi[i] > q_hi[i-1]:
        new_high[i] = True
    if q_lo[i] < q_lo[i-1]:
        new_low[i] = True

plot(q_hi.tolist(), title="Quarterly High", color="#4CAF50", linewidth=1)
plot(q_lo.tolist(), title="Quarterly Low", color="#f44336", linewidth=1)
plot(q_open.tolist(), title="Quarterly Open", color="#42a5f5", linewidth=1)

plotshape(new_high.tolist(), title="New High", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(new_low.tolist(), title="New Low", style="triangledown", location="abovebar", color="#ff1744", size="small")
