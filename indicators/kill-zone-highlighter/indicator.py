from tg_scripting import *
import numpy as np

indicator("Kill Zone Highlighter", overlay=True)

show_asia = input.bool(True, "Show Asian Session")
show_london = input.bool(True, "Show London Open")
show_ny = input.bool(True, "Show New York Open")
show_overlap = input.bool(True, "Show London/NY Overlap")
session_bars = input.int(8, "Session Length (bars)", minval=2, maxval=30)

n = len(close)
asia_zone = np.zeros(n, dtype=bool)
london_zone = np.zeros(n, dtype=bool)
ny_zone = np.zeros(n, dtype=bool)
overlap_zone = np.zeros(n, dtype=bool)

cycle = session_bars * 4
for i in range(n):
    pos = i % cycle
    if pos < session_bars:
        asia_zone[i] = True
    elif pos < session_bars * 2:
        london_zone[i] = True
        if pos >= int(session_bars * 1.5):
            overlap_zone[i] = True
    elif pos < session_bars * 3:
        ny_zone[i] = True
        if pos < int(session_bars * 2.5):
            overlap_zone[i] = True

vol_ma = ta.sma(volume, 20)
high_vol = np.array([volume[i] > vol_ma[i] * 1.2 if not np.isnan(vol_ma[i]) else False for i in range(n)], dtype=bool)

if show_asia:
    bgcolor(asia_zone, color="rgba(156,39,176,0.06)")
if show_london:
    bgcolor(london_zone, color="rgba(33,150,243,0.06)")
if show_ny:
    bgcolor(ny_zone, color="rgba(76,175,80,0.06)")
if show_overlap:
    bgcolor(overlap_zone, color="rgba(255,193,7,0.10)")

kill_active = np.array([
    (asia_zone[i] and show_asia) or (london_zone[i] and show_london) or
    (ny_zone[i] and show_ny) or (overlap_zone[i] and show_overlap)
    for i in range(n)
], dtype=bool)

hot_zone = np.array([kill_active[i] and high_vol[i] for i in range(n)], dtype=bool)
plotshape(hot_zone, title="High Vol Kill Zone", style="triangleup", location="belowbar", color="#ffd740")

plot(vol_ma, title="Volume MA", color="rgba(255,255,255,0.0)", linewidth=1)
