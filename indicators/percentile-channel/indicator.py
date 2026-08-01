from tg_scripting import *
import numpy as np

indicator("Percentile Channel", overlay=True)

length = input.int(50, "Channel Length", minval=10, maxval=200)
upper_pct = input.float(90.0, "Upper Percentile", minval=60.0, maxval=99.0, step=1.0)
lower_pct = input.float(10.0, "Lower Percentile", minval=1.0, maxval=40.0, step=1.0)
mid_pct = input.float(50.0, "Mid Percentile", minval=25.0, maxval=75.0, step=5.0)

src = np.array(close, dtype=float)
n = len(src)

upper_band = np.full(n, np.nan)
lower_band = np.full(n, np.nan)
mid_band = np.full(n, np.nan)
pct_rank = np.zeros(n)

for i in range(length, n):
    window = src[i - length:i + 1]
    upper_band[i] = np.percentile(window, upper_pct)
    lower_band[i] = np.percentile(window, lower_pct)
    mid_band[i] = np.percentile(window, mid_pct)
    pct_rank[i] = np.sum(window <= src[i]) / len(window) * 100.0

at_upper = pct_rank > upper_pct
at_lower = pct_rank < lower_pct

plot(upper_band.tolist(), title="Upper Band", color="#EF5350", linewidth=1)
plot(mid_band.tolist(), title="Mid Band", color="#FFD54F", linewidth=1)
plot(lower_band.tolist(), title="Lower Band", color="#66BB6A", linewidth=1)
bgcolor(at_upper, color="rgba(239,83,80,0.06)")
bgcolor(at_lower, color="rgba(102,187,106,0.06)")
plotshape(at_upper, title="Upper Touch", style="triangledown", location="abovebar", color="#EF5350")
plotshape(at_lower, title="Lower Touch", style="triangleup", location="belowbar", color="#66BB6A")
