from tg_scripting import *
import numpy as np

indicator("Expectancy Calculator", overlay=False)

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
smooth = input.int(10, "Smoothing", minval=1, maxval=30)

n = len(close)
expectancy = np.zeros(n)
win_rate = np.zeros(n)
avg_win = np.zeros(n)
avg_loss = np.zeros(n)
edge_ratio = np.zeros(n)

for i in range(1, n):
    start = max(1, i - lookback + 1)
    wins = []
    losses = []
    for j in range(start, i + 1):
        r = (close[j] - close[j - 1]) / close[j - 1] * 100.0
        if r > 0:
            wins.append(r)
        elif r < 0:
            losses.append(abs(r))

    total = len(wins) + len(losses)
    if total > 0 and len(wins) > 0 and len(losses) > 0:
        wr = len(wins) / total
        aw = np.mean(wins)
        al = np.mean(losses)
        win_rate[i] = wr * 100.0
        avg_win[i] = aw
        avg_loss[i] = al
        expectancy[i] = (wr * aw) - ((1 - wr) * al)
        edge_ratio[i] = aw / al if al > 0 else 0

smoothed = ta.sma(expectancy, smooth)
smooth_exp = np.zeros(n)
for i in range(n):
    smooth_exp[i] = smoothed[i] if not np.isnan(smoothed[i]) else 0


plot(expectancy, title="Expectancy", color="#42a5f5", linewidth=2)
plot(smooth_exp, title="Smoothed", color="#ffa726", linewidth=1)
plot(edge_ratio, title="Edge Ratio", color="#ab47bc", linewidth=1)
hline(0, title="Zero", color="#555555", linestyle="dashed")
