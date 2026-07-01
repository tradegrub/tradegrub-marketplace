from tg_scripting import *
import numpy as np

indicator("Time of Day Edge Analyzer", overlay=False)

num_bins = input.int(10, "Bar Position Bins", minval=4, maxval=50)
lookback = input.int(100, "Lookback Periods", minval=20, maxval=500)
show_avg = input.bool(True, "Show Average Return")

src_c = np.array(close, dtype=float)
src_o = np.array(open, dtype=float)
n = len(src_c)

returns = np.zeros(n)
for i in range(1, n):
    returns[i] = (src_c[i] - src_c[i - 1]) / (src_c[i - 1] + 1e-10) * 100.0

edge_score = np.full(n, np.nan)
avg_ret = np.full(n, np.nan)
win_rate = np.full(n, np.nan)

for i in range(lookback, n):
    pos = i % num_bins
    same_pos_rets = []
    for j in range(i - lookback, i):
        if j > 0 and j % num_bins == pos:
            same_pos_rets.append(returns[j])

    if len(same_pos_rets) >= 3:
        arr = np.array(same_pos_rets)
        mean_ret = np.mean(arr)
        std_ret = np.std(arr)
        avg_ret[i] = mean_ret
        win_rate[i] = np.sum(arr > 0) / len(arr) * 100.0
        edge_score[i] = mean_ret / (std_ret + 1e-10)

strong_bull = np.array([not np.isnan(edge_score[i]) and edge_score[i] > 0.5 for i in range(n)])
strong_bear = np.array([not np.isnan(edge_score[i]) and edge_score[i] < -0.5 for i in range(n)])

plot(edge_score, title="Edge Score", color="#AB47BC", linewidth=2)
if show_avg:
    plot(avg_ret, title="Avg Return %", color="#42A5F5", linewidth=1)
plot(win_rate, title="Win Rate %", color="#FFA726", linewidth=1)

hline(0, title="Zero", color="#555", linestyle="dashed")
hline(0.5, title="Bull Edge", color="rgba(76,175,80,0.3)", linestyle="dashed")
hline(-0.5, title="Bear Edge", color="rgba(239,83,80,0.3)", linestyle="dashed")

bgcolor(strong_bull, color="rgba(76,175,80,0.08)")
bgcolor(strong_bear, color="rgba(239,83,80,0.08)")
