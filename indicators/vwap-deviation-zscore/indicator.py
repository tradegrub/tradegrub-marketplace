from tg_scripting import *
import numpy as np

indicator("VWAP Deviation Z-Score", overlay=False)

length = input.int(50, "VWAP Length", minval=10, maxval=200)
zscore_len = input.int(20, "Z-Score Length", minval=5, maxval=100)
upper_z = input.float(2.0, "Upper Z Threshold", minval=0.5, maxval=4.0, step=0.1)
lower_z = input.float(-2.0, "Lower Z Threshold", minval=-4.0, maxval=-0.5, step=0.1)

src = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

typical = (hi + lo + src) / 3.0
cum_tp_vol = np.zeros(n)
cum_vol = np.zeros(n)
vwap_arr = np.zeros(n)

for i in range(n):
    start = max(0, i - length + 1)
    cum_tp_vol[i] = np.sum(typical[start:i+1] * vol[start:i+1])
    cum_vol[i] = np.sum(vol[start:i+1])
    vwap_arr[i] = cum_tp_vol[i] / cum_vol[i] if cum_vol[i] > 0 else typical[i]

deviation = src - vwap_arr

zscore = np.zeros(n)
for i in range(zscore_len, n):
    window = deviation[i - zscore_len:i+1]
    mu = np.mean(window)
    sigma = np.std(window)
    zscore[i] = (deviation[i] - mu) / sigma if sigma > 0 else 0.0

overbought = zscore > upper_z
oversold = zscore < lower_z

plot(zscore, title="VWAP Z-Score", color="#42A5F5", linewidth=2)
hline(upper_z, title="Overbought", color="#EF5350", linestyle="dashed")
hline(lower_z, title="Oversold", color="#66BB6A", linestyle="dashed")
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(overbought, color="rgba(239,83,80,0.08)")
bgcolor(oversold, color="rgba(102,187,106,0.08)")
plotshape(overbought, title="OB Signal", style="triangledown", location="abovebar", color="#EF5350")
plotshape(oversold, title="OS Signal", style="triangleup", location="belowbar", color="#66BB6A")
