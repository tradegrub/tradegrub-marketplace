from tg_scripting import *
import numpy as np

indicator("Volume Accumulation Divergence", overlay=False)

smooth_len = input.int(10, "OBV Smoothing", minval=3, maxval=30)
signal_len = input.int(5, "Signal Length", minval=2, maxval=15)
div_lookback = input.int(20, "Divergence Lookback", minval=10, maxval=50)

cl = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

obv = np.zeros(n)
for i in range(1, n):
    if cl[i] > cl[i-1]:
        obv[i] = obv[i-1] + vol[i]
    elif cl[i] < cl[i-1]:
        obv[i] = obv[i-1] - vol[i]
    else:
        obv[i] = obv[i-1]

obv_smooth = np.array(ta.ema(obv.tolist(), smooth_len), dtype=float)
obv_smooth = np.nan_to_num(obv_smooth, nan=0.0)

signal = np.array(ta.ema(obv_smooth.tolist(), signal_len), dtype=float)
signal = np.nan_to_num(signal, nan=0.0)

histogram = obv_smooth - signal

obv_norm = np.zeros(n)
for i in range(50, n):
    window = obv_smooth[i-50:i+1]
    mu = np.mean(window)
    std = np.std(window)
    if std > 0:
        obv_norm[i] = (obv_smooth[i] - mu) / std

bull_div = np.zeros(n, dtype=bool)
bear_div = np.zeros(n, dtype=bool)
for i in range(div_lookback, n):
    if cl[i] < cl[i-div_lookback] and obv_norm[i] > obv_norm[i-div_lookback]:
        bull_div[i] = True
    elif cl[i] > cl[i-div_lookback] and obv_norm[i] < obv_norm[i-div_lookback]:
        bear_div[i] = True

plot(obv_norm.tolist(), title="Smoothed OBV", color="#42a5f5", linewidth=2)
plot((histogram / max(np.std(histogram[50:]), 1e-10)).tolist(), title="Histogram", color="#78909C", style=plot.style_histogram)
hline(0, title="Zero", color="#888888", linestyle="dashed")
hline(2, title="Strong Acc", color="#4CAF50", linestyle="dashed")
hline(-2, title="Strong Dist", color="#f44336", linestyle="dashed")
plotshape(bull_div.tolist(), title="Bull Div", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bear_div.tolist(), title="Bear Div", style="triangledown", location="abovebar", color="#ff1744", size="small")
bgcolor(bull_div.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(bear_div.tolist(), color="rgba(244,67,54,0.08)")
