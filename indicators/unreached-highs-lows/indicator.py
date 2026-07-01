from tg_scripting import *
import numpy as np

lookback = input.int(30, "Lookback Period", minval=5, maxval=100)

h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
n = len(h)

uh_pct = np.full(n, np.nan)
ul_pct = np.full(n, np.nan)

for i in range(lookback, n):
    uh = 0
    ul = 0
    for j in range(i - lookback, i):
        subsequent_lows = l[j + 1:i + 1]
        if len(subsequent_lows) > 0 and np.all(subsequent_lows > h[j]):
            uh += 1
        subsequent_highs = h[j + 1:i + 1]
        if len(subsequent_highs) > 0 and np.all(subsequent_highs < l[j]):
            ul += 1
    uh_pct[i] = uh / lookback * 100.0
    ul_pct[i] = ul / lookback * 100.0

net_persistence = np.where(np.isnan(uh_pct), 0, uh_pct) - np.where(np.isnan(ul_pct), 0, ul_pct)

plot(uh_pct, title="Unreached Highs %", color="rgba(38,166,154,0.9)")
plot(ul_pct, title="Unreached Lows %", color="rgba(239,83,80,0.9)")
plot(net_persistence, title="Net Persistence", color="rgba(255,235,59,0.9)")
hline(50, title="Mid Level", color="rgba(128,128,128,0.4)")
hline(0, title="Zero Line", color="rgba(128,128,128,0.4)")
bgcolor(net_persistence > 30, color="rgba(38,166,154,0.08)")
bgcolor(net_persistence < -30, color="rgba(239,83,80,0.08)")
