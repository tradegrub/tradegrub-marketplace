from tg_scripting import *
import numpy as np

indicator("Adaptive Cycle Momentum", overlay=False)

length = input.int(20, "Cycle Length", minval=10, maxval=60)
smooth = input.int(5, "Smoothing", minval=2, maxval=15)
adapt_window = input.int(50, "Adaptive Window", minval=20, maxval=150)

cl = np.array(close, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, length), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

macd_l, macd_s, macd_h = ta.macd(close, 12, 26, 9)
macd_hist = np.array(macd_h, dtype=float)
macd_hist = np.nan_to_num(macd_hist, nan=0.0)

rsi_norm = (rsi_arr - 50) / 50
macd_norm = np.zeros(n)
for i in range(adapt_window, n):
    window = macd_hist[i-adapt_window:i]
    std = np.std(window)
    if std > 0:
        macd_norm[i] = macd_hist[i] / std

cycle_mom = rsi_norm * 0.5 + np.clip(macd_norm, -3, 3) / 3 * 0.5

smoothed = np.copy(cycle_mom)
alpha = 2.0 / (smooth + 1)
for i in range(1, n):
    smoothed[i] = alpha * cycle_mom[i] + (1 - alpha) * smoothed[i-1]

ob_level = np.zeros(n)
os_level = np.zeros(n)
for i in range(adapt_window, n):
    window = smoothed[i-adapt_window:i]
    std = np.std(window)
    ob_level[i] = np.mean(window) + 1.5 * std
    os_level[i] = np.mean(window) - 1.5 * std

bull_zone = smoothed < os_level
bear_zone = smoothed > ob_level

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if smoothed[i] > 0 and smoothed[i-1] <= 0:
        cross_up[i] = True
    elif smoothed[i] < 0 and smoothed[i-1] >= 0:
        cross_down[i] = True

plot(smoothed.tolist(), title="Cycle Momentum", color="#26c6da", linewidth=2)
plot(ob_level.tolist(), title="Upper Band", color="#f44336", linewidth=1)
plot(os_level.tolist(), title="Lower Band", color="#4CAF50", linewidth=1)
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(bull_zone.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(bear_zone.tolist(), color="rgba(244,67,54,0.08)")
plotshape(cross_up.tolist(), title="Bull Cross", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Bear Cross", style="triangledown", location="abovebar", color="#ff1744", size="small")
