from tg_scripting import *
import numpy as np

indicator("Market Structure Shift Detector", overlay=True)

swing_len = input.int(5, "Swing Length", minval=2, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_lines = input.bool(True, "Show Structure Lines")

n = len(close)

# Identify swing highs and lows
swing_hi = np.full(n, np.nan)
swing_lo = np.full(n, np.nan)
hi_indices = []
lo_indices = []

for i in range(swing_len, n - swing_len):
    if high[i] == max(high[max(0, i - swing_len):i + swing_len + 1]):
        swing_hi[i] = float(high[i])
        hi_indices.append(i)
    if low[i] == min(low[max(0, i - swing_len):i + swing_len + 1]):
        swing_lo[i] = float(low[i])
        lo_indices.append(i)

# Track structure: HH/HL = bullish, LH/LL = bearish
mss_bull = np.zeros(n, dtype=bool)
mss_bear = np.zeros(n, dtype=bool)
trend = np.zeros(n)  # 1=bullish, -1=bearish

prev_trend = 0
last_hi = None
last_lo = None
prev_hi = None
prev_lo = None

for i in range(n):
    if not np.isnan(swing_hi[i]):
        prev_hi = last_hi
        last_hi = float(swing_hi[i])
    if not np.isnan(swing_lo[i]):
        prev_lo = last_lo
        last_lo = float(swing_lo[i])

    cur_trend = prev_trend
    if prev_hi is not None and last_hi is not None and prev_lo is not None and last_lo is not None:
        if last_hi > prev_hi and last_lo > prev_lo:
            cur_trend = 1
        elif last_hi < prev_hi and last_lo < prev_lo:
            cur_trend = -1

    # Detect shift
    if cur_trend != prev_trend and prev_trend != 0:
        if cur_trend == 1 and prev_trend == -1:
            mss_bull[i] = True
        elif cur_trend == -1 and prev_trend == 1:
            mss_bear[i] = True

    trend[i] = cur_trend
    prev_trend = cur_trend

bull_trend = trend > 0
bear_trend = trend < 0

bgcolor(bull_trend, color="rgba(0,230,118,0.04)")
bgcolor(bear_trend, color="rgba(255,23,68,0.04)")

plotshape(mss_bull, title="Bullish MSS", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(mss_bear, title="Bearish MSS", shape="triangledown", location="abovebar", color="#ff1744", size="small")

plot(trend, title="Trend", color="#42A5F5", display="none")

if show_labels:
    for i in range(n):
        if mss_bull[i]:
            label.new(x=i, y=float(low[i]), text="MSS Bull",
                      style=label.style_label_up, color="rgba(0,230,118,0.5)",
                      textcolor="#00e676", size="small")
        elif mss_bear[i]:
            label.new(x=i, y=float(high[i]), text="MSS Bear",
                      style=label.style_label_down, color="rgba(255,23,68,0.5)",
                      textcolor="#ff1744", size="small")

if show_lines:
    for i in range(n):
        if mss_bull[i] and last_lo is not None:
            line.new(x1=max(0, i - swing_len * 2), y1=float(low[i]),
                     x2=i, y2=float(low[i]),
                     color="#00e676", width=2, style=line.style_dashed)
        elif mss_bear[i] and last_hi is not None:
            line.new(x1=max(0, i - swing_len * 2), y1=float(high[i]),
                     x2=i, y2=float(high[i]),
                     color="#ff1744", width=2, style=line.style_dashed)
