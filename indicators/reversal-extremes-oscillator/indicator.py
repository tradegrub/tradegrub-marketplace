from tg_scripting import *
import numpy as np
from scipy.stats import percentileofscore

indicator("Reversal Extremes Oscillator", overlay=False)

mom_len = input.int(14, "Momentum Length", minval=5, maxval=50)
vol_len = input.int(20, "Volatility Length", minval=10, maxval=60)
lookback = input.int(100, "Historical Lookback", minval=50, maxval=252)
signal_len = input.int(5, "Signal Length", minval=2, maxval=15)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, mom_len), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

stoch_k, stoch_d = ta.stoch(high, low, close, mom_len, 3, 3)
sk = np.array(stoch_k, dtype=float)
sk = np.nan_to_num(sk, nan=50.0)

atr_arr = np.array(ta.atr(high, low, close, vol_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

mom_score = (rsi_arr - 50) / 50 * 0.5 + (sk - 50) / 50 * 0.5

vol_pct = np.zeros(n)
for i in range(lookback, n):
    window = atr_arr[i-lookback:i]
    vol_pct[i] = percentileofscore(window, atr_arr[i]) / 100

price_pos = np.zeros(n)
for i in range(vol_len, n):
    hh = np.max(hi[i-vol_len:i+1])
    ll = np.min(lo[i-vol_len:i+1])
    rng = hh - ll
    if rng > 0:
        price_pos[i] = (cl[i] - ll) / rng * 2 - 1

composite = mom_score * 0.4 + price_pos * 0.3 + (vol_pct - 0.5) * 0.6
composite_smooth = np.array(ta.sma(composite.tolist(), signal_len), dtype=float)
composite_smooth = np.nan_to_num(composite_smooth, nan=0.0)

signal = np.array(ta.sma(composite_smooth.tolist(), signal_len * 2), dtype=float)
signal = np.nan_to_num(signal, nan=0.0)

strength = np.zeros(n)
for i in range(lookback, n):
    window = np.abs(composite_smooth[i-lookback:i])
    if np.std(window) > 0:
        strength[i] = min(abs(composite_smooth[i]) / max(np.std(window), 1e-10) * 30, 100)

extreme_bull = composite_smooth < -0.5
extreme_bear = composite_smooth > 0.5

plot(composite_smooth.tolist(), title="Reversal Score", color="#e040fb", linewidth=2)
plot(signal.tolist(), title="Signal", color="#78909C", linewidth=1)
plot((strength / 100).tolist(), title="Strength", color="#ff9800", linewidth=1)
hline(0.5, title="Bearish Extreme", color="#f44336", linestyle="dashed")
hline(-0.5, title="Bullish Extreme", color="#4CAF50", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(extreme_bull.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(extreme_bear.tolist(), color="rgba(244,67,54,0.08)")
