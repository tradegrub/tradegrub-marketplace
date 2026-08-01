from tg_scripting import *
import numpy as np

lookback = input.int(100, "Lookback", minval=20, maxval=500)
fill_window = input.int(20, "Fill Window", minval=5, maxval=100)

n = len(close)
close_arr = np.array([float(close[i]) for i in range(n)])
open_arr = np.array([float(open[i]) for i in range(n)])
high_arr = np.array([float(high[i]) for i in range(n)])
low_arr = np.array([float(low[i]) for i in range(n)])

prev_close = np.roll(close_arr, 1)
prev_close[0] = close_arr[0]

# Detect gaps
gap_up = open_arr > prev_close * 1.001
gap_down = open_arr < prev_close * 0.999
has_gap = gap_up | gap_down

# Track gap fill status
gap_filled = np.zeros(n, dtype=bool)
unfilled_gap = np.zeros(n, dtype=bool)

for i in range(1, n):
    if not bool(has_gap[i]):
        continue
    target = float(prev_close[i])
    filled = False
    end_j = min(i + fill_window, n)
    for j in range(i, end_j):
        if bool(gap_up[i]) and float(low_arr[j]) <= target:
            filled = True
            break
        elif bool(gap_down[i]) and float(high_arr[j]) >= target:
            filled = True
            break
    gap_filled[i] = filled
    if not filled:
        unfilled_gap[i] = True

# Compute rolling fill probability
fill_prob = np.zeros(n)
for i in range(fill_window, n):
    start = max(0, i - lookback)
    gap_mask = has_gap[start:i + 1]
    total_gaps = np.sum(gap_mask)
    if total_gaps > 0:
        filled_gaps = np.sum(gap_filled[start:i + 1] & gap_mask)
        fill_prob[i] = float(filled_gaps) / float(total_gaps) * 100.0
    else:
        fill_prob[i] = float(fill_prob[i - 1]) if i > 0 else 50.0

# Gap size as percentage
gap_size = np.abs(open_arr - prev_close) / (prev_close + 0.0001) * 100.0
gap_size[~has_gap] = 0.0

plot(fill_prob, title="Fill Probability %", color="#2196F3")
plot(gap_size * 10, title="Gap Size (x10)", color="#FF9800")
hline(50, title="50%", color="rgba(128,128,128,0.4)")
hline(80, title="High Fill Rate", color="rgba(76,175,80,0.3)")
hline(20, title="Low Fill Rate", color="rgba(244,67,54,0.3)")

plotshape(unfilled_gap, title="Unfilled Gap", style="diamond", location="bottom", color="#F44336")
plotshape(gap_filled & has_gap, title="Filled Gap", style="triangleup", location="bottom", color="#4CAF50")
