from tg_scripting import *
import numpy as np

indicator("Kalman Spread Tracker", overlay=True)

process_noise = input.float(0.01, "Process Noise (Q)", minval=0.001, maxval=0.1, step=0.001)
measure_noise = input.float(1.0, "Measurement Noise (R)", minval=0.1, maxval=10.0, step=0.1)
spread_len = input.int(20, "Spread Z-Score Length", minval=5, maxval=100)
zscore_thresh = input.float(2.0, "Z-Score Threshold", minval=0.5, maxval=4.0, step=0.1)

src = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

# Use volume as proxy second series for spread
series_b = ta.sma(close, 50)
series_b = np.array(series_b, dtype=float)
series_b = np.where(np.isnan(series_b), src, series_b)

# Kalman filter for hedge ratio
hedge_ratio = np.zeros(n)
x = 1.0  # state estimate (hedge ratio)
P = 1.0  # error covariance
Q = process_noise
R = measure_noise

for i in range(n):
    if series_b[i] == 0:
        hedge_ratio[i] = x
        continue
    # Predict
    x_pred = x
    P_pred = P + Q
    # Update
    y = src[i] - x_pred * series_b[i]
    S = series_b[i] ** 2 * P_pred + R
    K = P_pred * series_b[i] / S if S != 0 else 0
    x = x_pred + K * y
    P = (1 - K * series_b[i]) * P_pred
    hedge_ratio[i] = x

# Compute spread
spread = src - hedge_ratio * series_b

# Z-score of spread
spread_zscore = np.zeros(n)
for i in range(spread_len, n):
    window = spread[i - spread_len:i + 1]
    mu = np.mean(window)
    sigma = np.std(window)
    spread_zscore[i] = (spread[i] - mu) / sigma if sigma > 0 else 0.0

long_signal = spread_zscore < -zscore_thresh
short_signal = spread_zscore > zscore_thresh

plot(spread_zscore.tolist(), title="Spread Z-Score", color="#42A5F5", linewidth=2)
plot(hedge_ratio.tolist(), title="Hedge Ratio", color="#FFD54F", linewidth=1)
hline(zscore_thresh, title="Upper", color="#EF5350", linestyle="dashed")
hline(-zscore_thresh, title="Lower", color="#66BB6A", linestyle="dashed")
hline(0.0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(long_signal, color="rgba(102,187,106,0.08)")
bgcolor(short_signal, color="rgba(239,83,80,0.08)")
plotshape(long_signal, title="Long Spread", style="triangleup", location="belowbar", color="#66BB6A")
plotshape(short_signal, title="Short Spread", style="triangledown", location="abovebar", color="#EF5350")
