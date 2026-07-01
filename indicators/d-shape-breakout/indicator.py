from tg_scripting import *
import numpy as np

indicator("Arc Breakout Signals", overlay=True)

swing_length = input.int(10, "Swing Length", minval=3, maxval=50)
arc_bars = input.int(20, "Arc Bars Forward", minval=5, maxval=60)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

# Find swing highs and lows using rolling window
swing_highs = np.full(n, np.nan)
swing_lows = np.full(n, np.nan)

for i in range(swing_length, n - swing_length):
    window_hi = hi[i - swing_length:i + swing_length + 1]
    if hi[i] == np.max(window_hi):
        swing_highs[i] = hi[i]
    window_lo = lo[i - swing_length:i + swing_length + 1]
    if lo[i] == np.min(window_lo):
        swing_lows[i] = lo[i]

# Draw arcs from swing points and detect breakouts
breakout_up = np.zeros(n, dtype=bool)
breakout_down = np.zeros(n, dtype=bool)
arc_resist = np.full(n, np.nan)
arc_support = np.full(n, np.nan)

for i in range(swing_length, n):
    # Check resistance arcs from swing highs
    if not np.isnan(swing_highs[i]):
        pivot = float(swing_highs[i])
        atr_val = float(np.array(ta.atr(high, low, close, swing_length), dtype=float)[i])
        radius = atr_val * 2.0
        for j in range(1, min(arc_bars + 1, n - i)):
            t = j / arc_bars
            arc_y = pivot + radius * np.sqrt(max(0, 1.0 - (2.0 * t - 1.0) ** 2))
            idx = i + j
            if idx < n:
                if np.isnan(arc_resist[idx]) or arc_y < arc_resist[idx]:
                    arc_resist[idx] = arc_y
                if hi[idx] > arc_y and not breakout_up[idx]:
                    breakout_up[idx] = True
                # Draw arc segment
                if j > 1:
                    t_prev = (j - 1) / arc_bars
                    arc_y_prev = pivot + radius * np.sqrt(max(0, 1.0 - (2.0 * t_prev - 1.0) ** 2))
                    line.new(x1=i + j - 1, y1=arc_y_prev, x2=idx, y2=arc_y, color="#f4433680")

    # Check support arcs from swing lows
    if not np.isnan(swing_lows[i]):
        pivot = float(swing_lows[i])
        atr_val = float(np.array(ta.atr(high, low, close, swing_length), dtype=float)[i])
        radius = atr_val * 2.0
        for j in range(1, min(arc_bars + 1, n - i)):
            t = j / arc_bars
            arc_y = pivot - radius * np.sqrt(max(0, 1.0 - (2.0 * t - 1.0) ** 2))
            idx = i + j
            if idx < n:
                if np.isnan(arc_support[idx]) or arc_y > arc_support[idx]:
                    arc_support[idx] = arc_y
                if lo[idx] < arc_y and not breakout_down[idx]:
                    breakout_down[idx] = True
                if j > 1:
                    t_prev = (j - 1) / arc_bars
                    arc_y_prev = pivot - radius * np.sqrt(max(0, 1.0 - (2.0 * t_prev - 1.0) ** 2))
                    line.new(x1=i + j - 1, y1=arc_y_prev, x2=idx, y2=arc_y, color="#4CAF5080")

plotshape(breakout_up.tolist(), title="Breakout Up", style="triangleup", location="belowbar", color="#4CAF50")
plotshape(breakout_down.tolist(), title="Breakout Down", style="triangledown", location="abovebar", color="#f44336")
