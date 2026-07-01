from tg_scripting import *
import numpy as np

indicator("Trend Template Qualifier", overlay=False)

src = np.array(close, dtype=float)
n = len(src)

# Compute SMAs
def sma(data, length):
    out = np.full(len(data), np.nan)
    cs = np.cumsum(data)
    out[length - 1:] = (cs[length - 1:] - np.concatenate(([0], cs[:-length]))) / length
    return out

sma_150 = sma(src, 150)
sma_200 = sma(src, 200)

# 52-week (252 trading days) high and low
week52 = 252
rolling_high = np.full(n, np.nan)
rolling_low = np.full(n, np.nan)
for i in range(week52, n):
    rolling_high[i] = np.max(src[i - week52:i + 1])
    rolling_low[i] = np.min(src[i - week52:i + 1])

# RS proxy: price performance over lookback
rs_lookback = 252
rs_rating = np.full(n, np.nan)
for i in range(rs_lookback, n):
    rs_rating[i] = (src[i] / src[i - rs_lookback] - 1.0) * 100.0

score = np.zeros(n)
cond_all = np.zeros(n, dtype=bool)

for i in range(week52, n):
    s = 0

    # 1. Price > 150 SMA
    if not np.isnan(sma_150[i]) and src[i] > sma_150[i]:
        s += 1

    # 2. Price > 200 SMA
    if not np.isnan(sma_200[i]) and src[i] > sma_200[i]:
        s += 1

    # 3. 150 SMA > 200 SMA
    if not np.isnan(sma_150[i]) and not np.isnan(sma_200[i]) and sma_150[i] > sma_200[i]:
        s += 1

    # 4. Price > 52-week low by 30%+
    if not np.isnan(rolling_low[i]) and rolling_low[i] > 0 and src[i] >= rolling_low[i] * 1.30:
        s += 1

    # 5. Price within 25% of 52-week high
    if not np.isnan(rolling_high[i]) and rolling_high[i] > 0 and src[i] >= rolling_high[i] * 0.75:
        s += 1

    # 6. RS rating proxy > 0 (positive yearly performance)
    if not np.isnan(rs_rating[i]) and rs_rating[i] > 0:
        s += 1

    score[i] = s
    if s == 6:
        cond_all[i] = True

# Color histogram by score
colors = []
for i in range(n):
    s = int(score[i])
    if s == 6:
        colors.append("#00e676")
    elif s >= 4:
        colors.append("#66bb6a")
    elif s >= 2:
        colors.append("#ff9800")
    else:
        colors.append("#ef5350")

plot(score.tolist(), title="Template Score", color=colors, style=plot.style_histogram)
hline(6, title="All Conditions Met", color="#00e676", linestyle="dashed")
hline(3, title="Partial", color="#ff9800", linestyle="dotted")
bgcolor(cond_all.tolist(), color="rgba(0,230,118,0.1)")
