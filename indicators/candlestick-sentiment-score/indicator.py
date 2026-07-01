from tg_scripting import *
import numpy as np

indicator("Candlestick Sentiment Score", overlay=False)

lookback = input.int(10, "Scoring Lookback", minval=3, maxval=50)
smooth_len = input.int(5, "Smoothing Length", minval=1, maxval=20)
show_bars = input.bool(True, "Color Score Bars")

cl = np.array(close, dtype=np.float64)
op = np.array(open, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

raw_score = np.zeros(n)

for i in range(1, n):
    bar_range = hi[i] - lo[i]
    if bar_range == 0:
        raw_score[i] = 0.0
        continue

    body = cl[i] - op[i]
    body_pct = body / bar_range

    close_pos = (cl[i] - lo[i]) / bar_range * 2.0 - 1.0

    upper_wick = hi[i] - max(cl[i], op[i])
    lower_wick = min(cl[i], op[i]) - lo[i]
    wick_bias = (lower_wick - upper_wick) / bar_range

    raw_score[i] = (body_pct * 0.4 + close_pos * 0.4 + wick_bias * 0.2) * 100.0

# Rolling average
avg_score = np.zeros(n)
for i in range(lookback - 1, n):
    avg_score[i] = np.mean(raw_score[i - lookback + 1:i + 1])

# Smooth
smoothed = np.zeros(n)
if smooth_len > 1:
    kernel = np.ones(smooth_len) / smooth_len
    smoothed = np.convolve(avg_score, kernel, mode='same')
else:
    smoothed = avg_score.copy()

colors = []
for i in range(n):
    if smoothed[i] > 20:
        colors.append("#00e676")
    elif smoothed[i] > 0:
        colors.append("#66bb6a")
    elif smoothed[i] > -20:
        colors.append("#ef5350")
    else:
        colors.append("#ff1744")

if show_bars:
    plot(smoothed.tolist(), title="Sentiment", color=colors, linewidth=2, style="histogram")
else:
    plot(smoothed.tolist(), title="Sentiment", color="#2196F3", linewidth=2)

hline(0, title="Neutral", color="rgba(158,158,158,0.5)")
hline(30, title="Bullish", color="rgba(0,230,118,0.3)", linestyle="dashed")
hline(-30, title="Bearish", color="rgba(255,23,68,0.3)", linestyle="dashed")
