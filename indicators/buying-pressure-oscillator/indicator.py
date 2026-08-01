from tg_scripting import *
import numpy as np

indicator("Buying Pressure Oscillator", overlay=False)

length = input.int(14, "Wave Length", minval=5, maxval=40)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

bull_power = cl - lo
bear_power = hi - cl
total_range = hi - lo
total_range = np.where(total_range == 0, 1e-10, total_range)

buy_ratio = bull_power / total_range
sell_ratio = bear_power / total_range

buy_sum = np.zeros(n)
sell_sum = np.zeros(n)
for i in range(length, n):
    buy_sum[i] = np.sum(buy_ratio[i-length+1:i+1])
    sell_sum[i] = np.sum(sell_ratio[i-length+1:i+1])

wave = np.zeros(n)
for i in range(length, n):
    total = buy_sum[i] + sell_sum[i]
    if total > 0:
        wave[i] = (buy_sum[i] - sell_sum[i]) / total * 100

smoothed = np.array(ta.sma(wave.tolist(), smooth), dtype=float)
smoothed = np.nan_to_num(smoothed, nan=0.0)

ob = smoothed > 40
os_zone = smoothed < -40

plot(smoothed.tolist(), title="Buying Pressure", color="#42a5f5", linewidth=2)
hline(40, title="Overbought", color="#f44336", linestyle="dashed")
hline(-40, title="Oversold", color="#4CAF50", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(ob.tolist(), color="rgba(244,67,54,0.06)")
bgcolor(os_zone.tolist(), color="rgba(76,175,80,0.06)")
