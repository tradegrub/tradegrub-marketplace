from tg_scripting import *
import numpy as np

indicator("Annual Range Reference", overlay=True)

period = input.int(252, "Annual Period", minval=100, maxval=300)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

ann_hi = np.zeros(n)
ann_lo = np.zeros(n)
ann_open = np.zeros(n)

for i in range(period, n):
    ann_hi[i] = np.max(hi[i-period:i+1])
    ann_lo[i] = np.min(lo[i-period:i+1])
    ann_open[i] = cl[i-period]

ann_mid = (ann_hi + ann_lo) / 2
pct_range = np.where(ann_lo > 0, (cl - ann_lo) / (ann_hi - ann_lo) * 100, 50.0)

plot(ann_hi[period:].tolist() if n > period else [], title="Annual High", color="#4CAF50", linewidth=1)
plot(ann_lo[period:].tolist() if n > period else [], title="Annual Low", color="#f44336", linewidth=1)
plot(ann_open[period:].tolist() if n > period else [], title="Annual Open", color="#42a5f5", linewidth=1)
plot(ann_mid[period:].tolist() if n > period else [], title="Annual Mid", color="#888888", linewidth=1)

valid = ann_hi > 0

if n > period + 5:
    label.new(x=n-1, y=float(ann_hi[n-1]),
              text=f"52wk Hi: {ann_hi[n-1]:.2f}",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#4CAF50", size="small")
    label.new(x=n-1, y=float(ann_lo[n-1]),
              text=f"52wk Lo: {ann_lo[n-1]:.2f}",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#f44336", size="small")
