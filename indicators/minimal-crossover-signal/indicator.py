from tg_scripting import *
import numpy as np

indicator("Minimal Crossover Signal", overlay=False)

length = input.int(14, "Signal Length", minval=5, maxval=50)

cl = np.array(close, dtype=float)
n = len(cl)

sma = np.array(ta.sma(close, length), dtype=float)
ema = np.array(ta.ema(close, length), dtype=float)
sma = np.nan_to_num(sma, nan=0.0)
ema = np.nan_to_num(ema, nan=0.0)

wma = np.zeros(n)
for i in range(length, n):
    weights = np.arange(1, length + 1, dtype=float)
    wma[i] = np.sum(cl[i-length+1:i+1] * weights) / np.sum(weights)

sma_sig = np.where(sma > 0, (cl - sma) / np.maximum(sma, 1e-10) * 100, 0)
ema_sig = np.where(ema > 0, (cl - ema) / np.maximum(ema, 1e-10) * 100, 0)
wma_sig = np.where(wma > 0, (cl - wma) / np.maximum(wma, 1e-10) * 100, 0)

composite = (sma_sig + ema_sig + wma_sig) / 3.0

smoothed = np.array(ta.sma(composite.tolist(), 3), dtype=float)
smoothed = np.nan_to_num(smoothed, nan=0.0)


plot(smoothed.tolist(), title="Crossover Signal", color="#e040fb", linewidth=2)
hline(0.5, title="Bullish", color="#4CAF50", linestyle="dashed")
hline(-0.5, title="Bearish", color="#f44336", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
