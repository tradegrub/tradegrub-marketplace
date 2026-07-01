from tg_scripting import *
import numpy as np

indicator("McGinley Dynamic Indicator", overlay=True)

length = input.int(14, "Length", minval=2, maxval=200)
k_factor = input.float(0.6, "K Factor", minval=0.1, maxval=2.0, step=0.1)

src = np.array(close)
n = len(src)

md = np.full(n, np.nan)
md[0] = src[0]

for i in range(1, n):
    prev = md[i - 1]
    if np.isnan(prev):
        md[i] = src[i]
        continue
    ratio = src[i] / prev if prev != 0 else 1.0
    denom = length * (ratio ** 4) * k_factor
    if denom == 0:
        denom = 1.0
    md[i] = prev + (src[i] - prev) / denom

# Compare with SMA for reference
sma_line = ta.sma(close, length)

# Trend
trend_up = np.zeros(n, dtype=bool)
trend_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if not np.isnan(md[i]) and not np.isnan(md[i - 1]):
        if md[i] > md[i - 1]:
            trend_up[i] = True
        else:
            trend_down[i] = True

plot(md.tolist(), title="McGinley Dynamic", color="#42A5F5", linewidth=2)
plot(sma_line, title="SMA Reference", color="rgba(255,255,255,0.2)", linewidth=1)
bgcolor(trend_down, color="rgba(255,23,68,0.04)")
