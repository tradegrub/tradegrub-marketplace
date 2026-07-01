from tg_scripting import *
import numpy as np

indicator("Ulcer Index", overlay=False)

length = input.int(14, "Length", minval=5, maxval=100)
show_dd = input.bool(True, "Show Drawdown %")

c = np.array(close, dtype=float)
n = len(c)

rolling_max = np.full(n, np.nan)
pct_dd = np.full(n, 0.0)
ulcer = np.full(n, np.nan)

for i in range(n):
    start = max(0, i - length + 1)
    rolling_max[i] = np.max(c[start:i + 1])
    pct_dd[i] = ((c[i] - rolling_max[i]) / rolling_max[i]) * 100.0

for i in range(length - 1, n):
    window = pct_dd[i - length + 1:i + 1]
    ulcer[i] = np.sqrt(np.mean(window ** 2))

stress = np.nanpercentile(ulcer[~np.isnan(ulcer)], 80) if np.any(~np.isnan(ulcer)) else 5.0
is_stress = np.array([not np.isnan(ulcer[i]) and ulcer[i] > stress for i in range(n)])

plot(ulcer, title="Ulcer Index", color="#AB47BC", linewidth=2)
if show_dd:
    plot(pct_dd, title="Drawdown %", color="#EF5350", linewidth=1)
hline(stress, title="Stress Level", color="#FF9800", linestyle="dashed")
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(is_stress, color="rgba(244,67,54,0.08)")
