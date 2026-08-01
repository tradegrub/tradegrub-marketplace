from tg_scripting import *
import numpy as np

indicator("Rolling Performance Dashboard", overlay=False)

cl = np.array(close, dtype=float)
n = len(cl)

periods = [5, 10, 20, 50, 100]
colors = ["#29b6f6", "#42a5f5", "#66bb6a", "#ff9800", "#ef5350"]

returns = {}
for p in periods:
    ret = np.zeros(n)
    for i in range(p, n):
        ret[i] = (cl[i] - cl[i-p]) / max(cl[i-p], 1e-10) * 100
    returns[p] = ret

for idx, p in enumerate(periods):
    plot(returns[p].tolist(), title=f"{p}-bar Return %", color=colors[idx], linewidth=1 if idx > 0 else 2)

hline(0, title="Zero", color="#888888", linestyle="dashed")

all_positive = np.ones(n, dtype=bool)
all_negative = np.ones(n, dtype=bool)
for p in periods:
    all_positive &= returns[p] > 0
    all_negative &= returns[p] < 0

bgcolor(all_positive.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(all_negative.tolist(), color="rgba(244,67,54,0.08)")

if n > 100:
    label.new(x=n-1, y=float(returns[5][n-1]),
              text=f"5d: {returns[5][n-1]:.1f}%",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#29b6f6", size="tiny")
    label.new(x=n-1, y=float(returns[20][n-1]),
              text=f"20d: {returns[20][n-1]:.1f}%",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#66bb6a", size="tiny")
