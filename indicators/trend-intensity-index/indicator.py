from tg_scripting import *
import numpy as np

indicator("Trend Intensity Index", overlay=False)

length = input.int(20, "Period", minval=5, maxval=100)
ma_type = input.int(1, "MA Type (1=SMA 2=EMA)", minval=1, maxval=2)
overbought = input.float(80.0, "Overbought", minval=50.0, maxval=100.0)
oversold = input.float(20.0, "Oversold", minval=0.0, maxval=50.0)

if ma_type == 1:
    ma = ta.sma(close, length)
else:
    ma = ta.ema(close, length)

n = len(close)
tii = np.full(n, 50.0)

for i in range(length, n):
    up_count = 0
    down_count = 0
    for j in range(i - length + 1, i + 1):
        if close[j] > ma[j]:
            up_count += 1
        elif close[j] < ma[j]:
            down_count += 1
    total = up_count + down_count
    if total > 0:
        tii[i] = (up_count / total) * 100.0

tii_smooth = ta.ema(tii, 5)


plot(tii_smooth, title="TII", color="#42A5F5", linewidth=2)
hline(overbought, title="Overbought", color="#4CAF50", linestyle="dashed")
hline(oversold, title="Oversold", color="#ff5252", linestyle="dashed")
hline(50.0, title="Midline", color="#666666", linestyle="dashed")

