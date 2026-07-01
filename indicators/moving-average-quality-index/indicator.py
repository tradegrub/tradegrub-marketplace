from tg_scripting import *
import numpy as np

indicator("Moving Average Quality Index", overlay=False)

length = input.int(20, "MA Length", minval=5, maxval=100)

cl = np.array(close, dtype=float)
n = len(cl)

sma = np.array(ta.sma(close, length), dtype=float)
ema = np.array(ta.ema(close, length), dtype=float)
sma = np.nan_to_num(sma, nan=0.0)
ema = np.nan_to_num(ema, nan=0.0)

dema = 2 * ema - np.array(ta.ema(ema.tolist(), length), dtype=float)
dema = np.nan_to_num(dema, nan=0.0)

def measure_smoothness(ma_vals, window=20):
    smoothness = np.zeros(n)
    for i in range(window, n):
        segment = ma_vals[i-window:i+1]
        if len(segment) > 1:
            diffs = np.diff(segment)
            smoothness[i] = 1.0 / (1.0 + np.std(diffs) * 100 / max(abs(np.mean(segment)), 1e-10))
    return smoothness * 100

def measure_lag(ma_vals, window=20):
    lag = np.zeros(n)
    for i in range(window, n):
        corr_vals = []
        for shift in range(1, min(window, 10)):
            if i - shift >= 0:
                a = cl[i-window:i+1-shift]
                b = ma_vals[i-window+shift:i+1]
                min_len = min(len(a), len(b))
                if min_len > 2:
                    r = np.corrcoef(a[:min_len], b[:min_len])[0, 1]
                    if not np.isnan(r):
                        corr_vals.append((shift, r))
        if corr_vals:
            best = max(corr_vals, key=lambda x: x[1])
            lag[i] = best[0]
    return lag

sma_smooth = measure_smoothness(sma)
ema_smooth = measure_smoothness(ema)
dema_smooth = measure_smoothness(dema)

plot(sma_smooth.tolist(), title="SMA Smoothness", color="#42a5f5", linewidth=2)
plot(ema_smooth.tolist(), title="EMA Smoothness", color="#ff9800", linewidth=2)
plot(dema_smooth.tolist(), title="DEMA Smoothness", color="#ab47bc", linewidth=2)
hline(50, title="Mid Quality", color="#888888", linestyle="dashed")
