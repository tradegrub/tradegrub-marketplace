from tg_scripting import *
import numpy as np
from scipy.signal import lfilter

indicator("Trend Regime Classifier", overlay=False)

fast_len = input.int(10, "Fast Period", minval=3, maxval=30)
slow_len = input.int(40, "Slow Period", minval=20, maxval=100)
regime_len = input.int(30, "Regime Window", minval=15, maxval=80)

cl = np.array(close, dtype=float)
n = len(cl)

b_fast = np.ones(fast_len) / fast_len
b_slow = np.ones(slow_len) / slow_len
fast_ma = lfilter(b_fast, 1, cl)
slow_ma = lfilter(b_slow, 1, cl)

trend_score = np.zeros(n)
for i in range(slow_len, n):
    fast_slope = (fast_ma[i] - fast_ma[max(0, i-5)]) / max(abs(fast_ma[max(0, i-5)]), 1e-10)
    slow_slope = (slow_ma[i] - slow_ma[max(0, i-5)]) / max(abs(slow_ma[max(0, i-5)]), 1e-10)
    spread = (fast_ma[i] - slow_ma[i]) / max(abs(slow_ma[i]), 1e-10)
    trend_score[i] = (fast_slope * 500 + slow_slope * 300 + spread * 200) / 3

smoothed = np.array(ta.sma(trend_score.tolist(), 5), dtype=float)
smoothed = np.nan_to_num(smoothed, nan=0.0)

regime = np.zeros(n, dtype=int)
for i in range(regime_len, n):
    window = smoothed[i-regime_len:i+1]
    std = np.std(window)
    mean = np.mean(window)
    if smoothed[i] > mean + 0.5 * std:
        regime[i] = 2  # Strong uptrend
    elif smoothed[i] > mean:
        regime[i] = 1  # Mild uptrend
    elif smoothed[i] < mean - 0.5 * std:
        regime[i] = -2  # Strong downtrend
    elif smoothed[i] < mean:
        regime[i] = -1  # Mild downtrend

strong_up = regime == 2
strong_down = regime == -2

plot(smoothed.tolist(), title="Trend Score", color="#42a5f5", linewidth=2)
plot((regime.astype(float) * 25).tolist(), title="Regime", color="#ff9800", linewidth=1)
hline(0, title="Neutral", color="#888888", linestyle="dashed")
bgcolor(strong_up.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(strong_down.tolist(), color="rgba(244,67,54,0.08)")
