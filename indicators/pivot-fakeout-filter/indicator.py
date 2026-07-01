from tg_scripting import *
import numpy as np

indicator("Pivot Fakeout Filter", overlay=True)

pivot_period = input.int(20, "Pivot Period", minval=5, maxval=100)
fakeout_pct = input.float(0.3, "Fakeout Tolerance %", minval=0.05, maxval=2.0, step=0.05)
show_zones = input.bool(True, "Show Tolerance Zones")

hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
cl = np.array(close, dtype=np.float64)
n = len(cl)

tol = fakeout_pct / 100.0

prev_high = np.full(n, np.nan)
prev_low = np.full(n, np.nan)
prev_close = np.full(n, np.nan)

for i in range(pivot_period, n):
    prev_high[i] = np.max(hi[i - pivot_period:i])
    prev_low[i] = np.min(lo[i - pivot_period:i])
    prev_close[i] = cl[i - 1]

pp = (prev_high + prev_low + prev_close) / 3.0
r1 = 2.0 * pp - prev_low
s1 = 2.0 * pp - prev_high
r2 = pp + (prev_high - prev_low)
s2 = pp - (prev_high - prev_low)
r3 = prev_high + 2.0 * (pp - prev_low)
s3 = prev_low - 2.0 * (prev_high - pp)

plot(pp.tolist(), title="PP", color="#ffeb3b", linewidth=2)
plot(r1.tolist(), title="R1", color="#ef5350")
plot(r2.tolist(), title="R2", color="#e53935")
plot(r3.tolist(), title="R3", color="#b71c1c")
plot(s1.tolist(), title="S1", color="#66bb6a")
plot(s2.tolist(), title="S2", color="#43a047")
plot(s3.tolist(), title="S3", color="#1b5e20")

if show_zones:
    p_r1_upper = plot((r1 * (1.0 + tol)).tolist(), title="R1 Upper", color="rgba(239,83,80,0.3)")
    p_r1_lower = plot((r1 * (1.0 - tol)).tolist(), title="R1 Lower", color="rgba(239,83,80,0.3)")
    fill(p_r1_upper, p_r1_lower, color="rgba(239,83,80,0.08)")

    p_s1_upper = plot((s1 * (1.0 + tol)).tolist(), title="S1 Upper", color="rgba(102,187,106,0.3)")
    p_s1_lower = plot((s1 * (1.0 - tol)).tolist(), title="S1 Lower", color="rgba(102,187,106,0.3)")
    fill(p_s1_upper, p_s1_lower, color="rgba(102,187,106,0.08)")

bull_break = np.zeros(n, dtype=bool)
bear_break = np.zeros(n, dtype=bool)

for i in range(pivot_period, n):
    if not np.isnan(r1[i]) and cl[i] > r1[i] * (1.0 + tol):
        bull_break[i] = True
    if not np.isnan(s1[i]) and cl[i] < s1[i] * (1.0 - tol):
        bear_break[i] = True

plotshape(bull_break.tolist(), title="Bullish Breakout", style="triangleup",
          location="belowbar", color="#00e676", size="small")
plotshape(bear_break.tolist(), title="Bearish Breakdown", style="triangledown",
          location="abovebar", color="#ff1744", size="small")
