from tg_scripting import *
import numpy as np

indicator("Trend Volatility Pulse", overlay=False)

fast_len = input.int(8, "Fast Length", minval=3, maxval=20)
slow_len = input.int(21, "Slow Length", minval=10, maxval=60)
vol_len = input.int(14, "Volatility Length", minval=5, maxval=30)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

fast_ema = np.array(ta.ema(close, fast_len), dtype=float)
slow_ema = np.array(ta.ema(close, slow_len), dtype=float)
fast_ema = np.nan_to_num(fast_ema, nan=0.0)
slow_ema = np.nan_to_num(slow_ema, nan=0.0)

atr_arr = np.array(ta.atr(high, low, close, vol_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

trend_component = np.zeros(n)
for i in range(slow_len, n):
    if slow_ema[i] > 0:
        trend_component[i] = (fast_ema[i] - slow_ema[i]) / atr_arr[i] if atr_arr[i] > 0 else 0

vol_component = np.zeros(n)
for i in range(50, n):
    atr_mean = np.mean(atr_arr[i-50:i])
    if atr_mean > 0:
        vol_component[i] = (atr_arr[i] / atr_mean - 1) * 100

pulse = trend_component * 30 + vol_component * 0.3

smoothed = np.array(ta.sma(pulse.tolist(), 3), dtype=float)
smoothed = np.nan_to_num(smoothed, nan=0.0)

strong_trend = np.abs(smoothed) > 30
vol_spike = vol_component > 50

plot(smoothed.tolist(), title="Trend Pulse", color="#e040fb", linewidth=2)
plot(vol_component.tolist(), title="Vol Component", color="#78909C", linewidth=1)
hline(30, title="Strong Bull", color="#4CAF50", linestyle="dashed")
hline(-30, title="Strong Bear", color="#f44336", linestyle="dashed")
hline(0, title="Neutral", color="#888888", linestyle="dashed")
bgcolor((smoothed > 30).tolist(), color="rgba(76,175,80,0.08)")
bgcolor((smoothed < -30).tolist(), color="rgba(244,67,54,0.08)")
bgcolor(vol_spike.tolist(), color="rgba(255,152,0,0.06)")
