from tg_scripting import *
import numpy as np
from scipy.signal import argrelextrema

indicator("Cycle Channel Oscillator", overlay=False)

channel_len = input.int(20, "Channel Length", minval=10, maxval=60)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)
signal_len = input.int(7, "Signal Length", minval=3, maxval=15)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

upper = np.zeros(n)
lower = np.zeros(n)
mid = np.zeros(n)
for i in range(channel_len, n):
    upper[i] = np.max(hi[i-channel_len:i+1])
    lower[i] = np.min(lo[i-channel_len:i+1])
    mid[i] = (upper[i] + lower[i]) / 2

channel_width = upper - lower
osc = np.zeros(n)
for i in range(channel_len, n):
    if channel_width[i] > 0:
        osc[i] = (cl[i] - mid[i]) / (channel_width[i] / 2) * 100

smoothed = np.array(ta.sma(osc.tolist(), smooth), dtype=float)
smoothed = np.nan_to_num(smoothed, nan=0.0)

signal = np.array(ta.ema(smoothed.tolist(), signal_len), dtype=float)
signal = np.nan_to_num(signal, nan=0.0)

bull_div = np.zeros(n, dtype=bool)
bear_div = np.zeros(n, dtype=bool)
for i in range(30, n):
    if cl[i] < cl[i-20] and smoothed[i] > smoothed[i-20]:
        bull_div[i] = True
    elif cl[i] > cl[i-20] and smoothed[i] < smoothed[i-20]:
        bear_div[i] = True

ob = smoothed > 80
os_zone = smoothed < -80

plot(smoothed.tolist(), title="Channel Oscillator", color="#26c6da", linewidth=2)
plot(signal.tolist(), title="Signal", color="#ff9800", linewidth=1)
hline(80, title="Overbought", color="#f44336", linestyle="dashed")
hline(-80, title="Oversold", color="#4CAF50", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(ob.tolist(), color="rgba(244,67,54,0.06)")
bgcolor(os_zone.tolist(), color="rgba(76,175,80,0.06)")
plotshape(bull_div.tolist(), title="Bull Div", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bear_div.tolist(), title="Bear Div", style="triangledown", location="abovebar", color="#ff1744", size="small")
