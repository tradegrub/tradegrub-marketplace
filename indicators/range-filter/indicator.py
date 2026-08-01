from tg_scripting import *
import numpy as np

indicator("Range Filter", overlay=True)

length = input.int(20, "Length", minval=5, maxval=100)
multiplier = input.float(2.0, "Multiplier", minval=0.5, maxval=5.0, step=0.1)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, length), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=0.0)

smooth_range = np.zeros(n)
smooth_range[0] = atr_arr[0] * multiplier
alpha = 2.0 / (length + 1)
for i in range(1, n):
    smooth_range[i] = alpha * (atr_arr[i] * multiplier) + (1 - alpha) * smooth_range[i - 1]

filt = np.zeros(n)
filt[0] = cl[0]
direction = np.zeros(n, dtype=int)

for i in range(1, n):
    if cl[i] > filt[i - 1] + smooth_range[i]:
        filt[i] = cl[i] - smooth_range[i]
        direction[i] = 1
    elif cl[i] < filt[i - 1] - smooth_range[i]:
        filt[i] = cl[i] + smooth_range[i]
        direction[i] = -1
    else:
        filt[i] = filt[i - 1]
        direction[i] = direction[i - 1]

up_filter = np.where(direction == 1, filt, np.nan).tolist()
dn_filter = np.where(direction == -1, filt, np.nan).tolist()

up_change = np.zeros(n, dtype=bool)
dn_change = np.zeros(n, dtype=bool)
for i in range(1, n):
    if direction[i] == 1 and direction[i - 1] != 1:
        up_change[i] = True
    elif direction[i] == -1 and direction[i - 1] != -1:
        dn_change[i] = True

plot(up_filter, title="Filter Up", color="#4CAF50", linewidth=2)
plot(dn_filter, title="Filter Down", color="#f44336", linewidth=2)
plotshape(up_change.tolist(), title="Trend Up", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(dn_change.tolist(), title="Trend Down", style="triangledown", location="abovebar", color="#ff1744", size="small")
