from tg_scripting import *
import numpy as np

indicator("End of Day Momentum", overlay=False)

session_len = input.int(12, "Session Length (bars)", minval=4, maxval=50)
eod_bars = input.int(3, "EOD Bars to Measure", minval=1, maxval=10)
smooth = input.int(5, "Smoothing Period", minval=1, maxval=20)

n = len(close)
eod_mom = np.zeros(n)
next_open_change = np.zeros(n)
signal_line = np.zeros(n)
bullish = np.zeros(n, dtype=bool)
bearish = np.zeros(n, dtype=bool)

for i in range(session_len, n):
    session_end = i
    session_start = max(0, i - session_len + 1)
    eod_start = max(session_start, session_end - eod_bars + 1)
    if eod_start > 0:
        eod_mom[i] = (close[session_end] - close[eod_start]) / close[eod_start] * 100.0

    if i + 1 < n:
        next_open_change[i] = (open[i + 1] - close[i]) / close[i] * 100.0

smoothed = ta.sma(eod_mom, smooth)
for i in range(n):
    signal_line[i] = smoothed[i] if not np.isnan(smoothed[i]) else 0.0

for i in range(1, n):
    bullish[i] = eod_mom[i] > 0 and eod_mom[i] > signal_line[i]
    bearish[i] = eod_mom[i] < 0 and eod_mom[i] < signal_line[i]

plot(eod_mom, title="EOD Momentum", color="#42a5f5", linewidth=2)
plot(signal_line, title="Signal", color="#ffa726", linewidth=1)
hline(0, title="Zero", color="#555555", linestyle="dashed")
