from tg_scripting import *
import numpy as np
from scipy.stats import zscore as scipy_zscore

indicator("Multi-Oscillator Composite", overlay=False)

length = input.int(14, "Oscillator Length", minval=5, maxval=50)
smooth = input.int(3, "Composite Smoothing", minval=1, maxval=10)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, length), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

stoch_k, stoch_d = ta.stoch(high, low, close, length, 3, 3)
stoch_arr = np.array(stoch_k, dtype=float)
stoch_arr = np.nan_to_num(stoch_arr, nan=50.0)

tp = (hi + lo + cl) / 3.0
tp_sma = np.array(ta.sma(tp.tolist(), length), dtype=float)
tp_sma = np.nan_to_num(tp_sma, nan=0.0)
cci = np.zeros(n)
for i in range(length, n):
    window = tp[i-length+1:i+1]
    md = np.mean(np.abs(window - np.mean(window)))
    if md > 0:
        cci[i] = (tp[i] - tp_sma[i]) / (0.015 * md)

rsi_norm = (rsi_arr - 50) / 50
stoch_norm = (stoch_arr - 50) / 50
cci_norm = np.clip(cci / 200, -1, 1)

composite = (rsi_norm + stoch_norm + cci_norm) / 3.0
composite_smooth = np.array(ta.sma(composite.tolist(), smooth), dtype=float)
composite_smooth = np.nan_to_num(composite_smooth, nan=0.0)

ob = composite_smooth > 0.5
os_zone = composite_smooth < -0.5

plot(composite_smooth.tolist(), title="Composite", color="#e040fb", linewidth=2)
plot(rsi_norm.tolist(), title="RSI Norm", color="#42a5f5", linewidth=1)
plot(stoch_norm.tolist(), title="Stoch Norm", color="#ff9800", linewidth=1)
hline(0.5, title="Overbought", color="#4CAF50", linestyle="dashed")
hline(-0.5, title="Oversold", color="#f44336", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(ob.tolist(), color="rgba(76,175,80,0.06)")
bgcolor(os_zone.tolist(), color="rgba(244,67,54,0.06)")
