from tg_scripting import *
import numpy as np

indicator("HalfTrend Indicator", overlay=True)

length = input.int(2, "Channel Length", minval=1, maxval=50)
amplitude = input.float(2.0, "ATR Amplitude", minval=0.5, maxval=10.0, step=0.5)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, length), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=0.0)

highma = np.array(ta.highest(high, length), dtype=float)
lowma = np.array(ta.lowest(low, length), dtype=float)

trend_line = np.full(n, np.nan)
trend_dir = np.zeros(n, dtype=int)
bull_flip = [False] * n
bear_flip = [False] * n
trend_color = ["#26A69A"] * n

# Initialize
trend_dir[0] = 1
trend_line[0] = lowma[0] - atr_arr[0] * amplitude

for i in range(1, n):
    prev_dir = trend_dir[i - 1]
    prev_line = trend_line[i - 1]

    if prev_dir == 1:
        # Bullish: trend line rises with low channel minus ATR offset
        new_line = lowma[i] - atr_arr[i] * amplitude
        trend_line[i] = max(prev_line, new_line) if not np.isnan(prev_line) else new_line

        if cl[i] < trend_line[i]:
            # Flip to bearish
            trend_dir[i] = -1
            trend_line[i] = highma[i] + atr_arr[i] * amplitude
            bear_flip[i] = True
            trend_color[i] = "#EF5350"
        else:
            trend_dir[i] = 1
            trend_color[i] = "#26A69A"
    else:
        # Bearish: trend line falls with high channel plus ATR offset
        new_line = highma[i] + atr_arr[i] * amplitude
        trend_line[i] = min(prev_line, new_line) if not np.isnan(prev_line) else new_line

        if cl[i] > trend_line[i]:
            # Flip to bullish
            trend_dir[i] = 1
            trend_line[i] = lowma[i] - atr_arr[i] * amplitude
            bull_flip[i] = True
            trend_color[i] = "#26A69A"
        else:
            trend_dir[i] = -1
            trend_color[i] = "#EF5350"

plot(trend_line.tolist(), title="HalfTrend", color=trend_color)
plotshape(bull_flip, title="Bull Flip", style="triangleup", location="belowbar", color="#26A69A")
plotshape(bear_flip, title="Bear Flip", style="triangledown", location="abovebar", color="#EF5350")
