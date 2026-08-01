from tg_scripting import *
import numpy as np

indicator("Statistical Price Forecast", overlay=False)

stoch_len = input.int(14, "Stochastic Length", minval=5, maxval=30)
sma_len = input.int(20, "SMA Length", minval=10, maxval=50)
lookback = input.int(50, "History Lookback", minval=20, maxval=200)

cl = np.array(close, dtype=float)
n = len(cl)

stoch_k, stoch_d = ta.stoch(high, low, close, stoch_len, 3, 3)
sk = np.array(stoch_k, dtype=float)
sk = np.nan_to_num(sk, nan=50.0)

sma_arr = np.array(ta.sma(close, sma_len), dtype=float)
sma_arr = np.nan_to_num(sma_arr, nan=0.0)

sma_slope = np.zeros(n)
for i in range(5, n):
    if sma_arr[i-5] > 0:
        sma_slope[i] = (sma_arr[i] - sma_arr[i-5]) / sma_arr[i-5] * 100

stoch_score = (sk - 50) / 50
slope_score = np.clip(sma_slope * 10, -1, 1)
forecast = (stoch_score * 0.4 + slope_score * 0.6) * 100

conf = np.zeros(n)
start = max(lookback, sma_len + 10)
for i in range(start, n):
    window = forecast[i-lookback:i]
    if np.std(window) > 0:
        conf[i] = min(abs(forecast[i]) / max(np.std(window), 1e-10) * 30, 100)

plot(forecast.tolist(), title="Forecast Score", color="#e040fb", linewidth=2)
plot(conf.tolist(), title="Confidence", color="#78909C", linewidth=1)
hline(50, title="Strong Bull", color="#4CAF50", linestyle="dashed")
hline(-50, title="Strong Bear", color="#f44336", linestyle="dashed")
hline(0, title="Neutral", color="#888888", linestyle="dashed")

