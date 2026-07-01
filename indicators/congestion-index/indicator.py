from tg_scripting import *
import numpy as np

length = input.int(14, "Length", minval=2, maxval=100)

ln = int(length)

congestion = np.full(len(close), np.nan)

high_arr = np.array(high[:], dtype=float)
low_arr = np.array(low[:], dtype=float)

for i in range(len(close) - ln):
    # N-bar range: highest high - lowest low over the window
    n_range = np.max(high_arr[i:i + ln]) - np.min(low_arr[i:i + ln])
    # Sum of individual bar ranges
    bar_ranges = high_arr[i:i + ln] - low_arr[i:i + ln]
    sum_ranges = np.sum(bar_ranges)
    if sum_ranges > 1e-10:
        congestion[i] = (1.0 - n_range / sum_ranges) * 100.0
    else:
        congestion[i] = 0.0

plot(congestion, title="Congestion Index", color=color.purple)
hline(70, title="High Congestion", color=color.orange)
hline(30, title="Low Congestion", color=color.green)
bgcolor(congestion > 70, color="rgba(156,39,176,0.1)")
