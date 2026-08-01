from tg_scripting import *
import numpy as np

indicator("Stochastic Convergence Index", overlay=False)

fast = input.int(12, "MACD Fast", minval=5, maxval=30)
slow = input.int(26, "MACD Slow", minval=15, maxval=60)
signal_len = input.int(9, "Signal Length", minval=3, maxval=20)
stoch_len = input.int(14, "Stochastic Length", minval=5, maxval=30)
k_smooth = input.int(3, "K Smoothing", minval=1, maxval=10)

cl = np.array(close, dtype=float)
n = len(cl)

macd_l, macd_s, macd_h = ta.macd(close, fast, slow, signal_len)
macd_line = np.array(macd_l, dtype=float)
macd_line = np.nan_to_num(macd_line, nan=0.0)

stoch_macd = np.zeros(n)
for i in range(stoch_len, n):
    window = macd_line[i-stoch_len:i+1]
    hh = np.max(window)
    ll = np.min(window)
    if hh - ll > 0:
        stoch_macd[i] = (macd_line[i] - ll) / (hh - ll) * 100

k_line = np.array(ta.sma(stoch_macd.tolist(), k_smooth), dtype=float)
k_line = np.nan_to_num(k_line, nan=50.0)

d_line = np.array(ta.sma(k_line.tolist(), k_smooth), dtype=float)
d_line = np.nan_to_num(d_line, nan=50.0)

histogram = k_line - d_line

ob = k_line > 80
os_zone = k_line < 20

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if k_line[i] > d_line[i] and k_line[i-1] <= d_line[i-1]:
        cross_up[i] = True
    elif k_line[i] < d_line[i] and k_line[i-1] >= d_line[i-1]:
        cross_down[i] = True

plot(k_line.tolist(), title="%K", color="#26c6da", linewidth=2)
plot(d_line.tolist(), title="%D", color="#ff9800", linewidth=1)
plot(histogram.tolist(), title="Histogram", color="#78909C", style=plot.style_histogram)
hline(80, title="Overbought", color="#f44336", linestyle="dashed")
hline(20, title="Oversold", color="#4CAF50", linestyle="dashed")
hline(50, title="Mid", color="#888888", linestyle="dashed")
bgcolor(ob.tolist(), color="rgba(244,67,54,0.06)")
bgcolor(os_zone.tolist(), color="rgba(76,175,80,0.06)")
plotshape(cross_up.tolist(), title="Bull Cross", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Bear Cross", style="triangledown", location="abovebar", color="#ff1744", size="small")
