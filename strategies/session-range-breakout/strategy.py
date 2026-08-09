# Session Range Breakout — any session window, not just the regular-hours open.
from tg_scripting import *
import numpy as np

indicator("Session Range Breakout", overlay=True)

session_start = input.int(0, "Session start hour (UTC)", minval=0, maxval=23)
session_len = input.int(3, "Session length (hours)", minval=1, maxval=12)
buffer_pct = input.float(0.05, "Breakout buffer %", minval=0.0, maxval=1.0)
stop_at_opposite = input.bool(True, "Stop at opposite edge")
one_trade_per_session = input.bool(True, "One trade per session")

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
t = np.asarray(time, dtype=float)
n = len(c)

# Bar hour in UTC, derived from the millisecond timestamp so the window works
# on any instrument regardless of its home exchange.
hours = np.floor((t / 3600000.0) % 24).astype(int)
day_id = np.floor(t / 86400000.0).astype(int)

end_hour = (session_start + session_len) % 24
if session_start < end_hour:
    in_session = (hours >= session_start) & (hours < end_hour)
else:
    # Window wraps past midnight (Asia sessions do this routinely).
    in_session = (hours >= session_start) | (hours < end_hour)

range_hi = np.full(n, np.nan)
range_lo = np.full(n, np.nan)
long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)

cur_day = -1
cur_hi = -np.inf
cur_lo = np.inf
traded = False

for i in range(1, n):
    strategy.set_bar_index(i)

    if day_id[i] != cur_day:
        cur_day, cur_hi, cur_lo, traded = day_id[i], -np.inf, np.inf, False

    if in_session[i]:
        cur_hi = max(cur_hi, h[i])
        cur_lo = min(cur_lo, l[i])
        continue

    if cur_hi == -np.inf or cur_lo == np.inf:
        continue

    range_hi[i], range_lo[i] = cur_hi, cur_lo
    up_level = cur_hi * (1 + buffer_pct / 100)
    down_level = cur_lo * (1 - buffer_pct / 100)

    if traded and one_trade_per_session:
        continue

    if c[i] > up_level:
        strategy.entry("Long", strategy.LONG)
        long_sig[i] = True
        traded = True
    elif c[i] < down_level:
        strategy.entry("Short", strategy.SHORT)
        short_sig[i] = True
        traded = True

    if stop_at_opposite:
        if c[i] < cur_lo:
            strategy.close("Long")
        if c[i] > cur_hi:
            strategy.close("Short")

p1 = plot(range_hi, title="Session high", color="green")
p2 = plot(range_lo, title="Session low", color="red")
fill(p1, p2, color="rgba(66, 165, 245, 0.07)")

plotshape(long_sig, title="Break up", style="triangleup", location="belowbar", color="green")
plotshape(short_sig, title="Break down", style="triangledown", location="abovebar", color="red")
