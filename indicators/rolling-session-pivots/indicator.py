# Rolling Session Pivots — pivots that do not wait for tomorrow.
from tg_scripting import *
import numpy as np

indicator("Rolling Session Pivots", overlay=True)

window = input.int(24, "Rolling window (bars)", minval=4, maxval=500)
method = input.string("Classic", "Pivot formula", options=["Classic", "Fibonacci", "Camarilla"])
show_s3r3 = input.bool(False, "Show the third support and resistance")

h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
c = np.asarray(close, dtype=float)
n = len(c)

pp = np.full(n, np.nan)
r1 = np.full(n, np.nan); r2 = np.full(n, np.nan); r3 = np.full(n, np.nan)
s1 = np.full(n, np.nan); s2 = np.full(n, np.nan); s3 = np.full(n, np.nan)

for i in range(window, n):
    # The window ENDS at the previous bar, never the current one: a level that
    # moves with the bar it is meant to be judging is not a level.
    hi = float(np.nanmax(h[i - window:i]))
    lo = float(np.nanmin(l[i - window:i]))
    cl = float(c[i - 1])
    rng = hi - lo
    if not np.isfinite(rng) or rng <= 0:
        continue

    if method == "Fibonacci":
        p = (hi + lo + cl) / 3.0
        r1[i], s1[i] = p + 0.382 * rng, p - 0.382 * rng
        r2[i], s2[i] = p + 0.618 * rng, p - 0.618 * rng
        r3[i], s3[i] = p + rng, p - rng
    elif method == "Camarilla":
        p = (hi + lo + cl) / 3.0
        r1[i], s1[i] = cl + rng * 1.1 / 12.0, cl - rng * 1.1 / 12.0
        r2[i], s2[i] = cl + rng * 1.1 / 6.0, cl - rng * 1.1 / 6.0
        r3[i], s3[i] = cl + rng * 1.1 / 4.0, cl - rng * 1.1 / 4.0
    else:
        p = (hi + lo + cl) / 3.0
        r1[i], s1[i] = 2 * p - lo, 2 * p - hi
        r2[i], s2[i] = p + rng, p - rng
        r3[i], s3[i] = hi + 2 * (p - lo), lo - 2 * (hi - p)
    pp[i] = p

plot(pp, title="Pivot", color="orange")
plot(r1, title="R1", color="red")
plot(s1, title="S1", color="green")
plot(r2, title="R2", color="rgba(239,83,80,0.6)")
plot(s2, title="S2", color="rgba(0,230,118,0.6)")
if show_s3r3:
    plot(r3, title="R3", color="rgba(239,83,80,0.35)")
    plot(s3, title="S3", color="rgba(0,230,118,0.35)")
