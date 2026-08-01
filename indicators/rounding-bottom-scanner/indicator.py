from tg_scripting import *
import numpy as np

indicator("Rounding Bottom Scanner", overlay=False)

lookback = input.int(40, "Lookback Window", minval=20, maxval=100)
curvature_thresh = input.int(60, "Curvature Threshold", minval=10, maxval=100)
vol_confirm = input.int(1, "Volume Confirmation (1=On 0=Off)", minval=0, maxval=1)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

sma_slow = np.array(ta.sma(close, lookback), dtype=float)

score = np.zeros(n)
breakout = np.zeros(n, dtype=bool)

for i in range(lookback, n):
    window = cl[i - lookback:i]
    w_vol = vol[i - lookback:i]
    half = lookback // 2

    left = window[:half]
    right = window[half:]

    # Left slope (should be negative / declining)
    x_left = np.arange(half, dtype=float)
    left_slope = 0.0
    if np.std(x_left) > 0 and np.std(left) > 0:
        left_slope = np.corrcoef(x_left, left)[0, 1] * np.std(left) / np.std(x_left)

    # Right slope (should be positive / rising)
    x_right = np.arange(len(right), dtype=float)
    right_slope = 0.0
    if np.std(x_right) > 0 and np.std(right) > 0:
        right_slope = np.corrcoef(x_right, right)[0, 1] * np.std(right) / np.std(x_right)

    # Lowest point should be near center
    min_idx = int(np.argmin(window))
    center_dist = abs(min_idx - half) / half
    center_score = max(0.0, 1.0 - center_dist)

    # Curvature: fit quadratic, positive a = concave up
    x_full = np.arange(lookback, dtype=float)
    coeffs = np.polyfit(x_full, window, 2)
    curvature = coeffs[0]

    # Normalize curvature to 0-100
    price_range = np.max(window) - np.min(window)
    if price_range > 0:
        curv_norm = min(1.0, max(0.0, curvature * lookback * lookback / price_range))
    else:
        curv_norm = 0.0

    # Slope score: left down + right up
    slope_score = 0.0
    if left_slope < 0 and right_slope > 0:
        slope_score = 1.0
    elif left_slope < 0 or right_slope > 0:
        slope_score = 0.5

    # Volume profile
    vol_score = 1.0
    if vol_confirm == 1 and np.sum(w_vol) > 0:
        left_vol = w_vol[:half]
        right_vol = w_vol[half:]
        left_avg = np.mean(left_vol)
        right_avg = np.mean(right_vol)
        # Right side volume should be increasing toward end
        right_end = np.mean(right_vol[len(right_vol)//2:])
        right_start = np.mean(right_vol[:len(right_vol)//2])
        vol_rising = 1.0 if right_end > right_start else 0.5
        # Left side volume declining
        left_start_v = np.mean(left_vol[:len(left_vol)//2])
        left_end_v = np.mean(left_vol[len(left_vol)//2:])
        vol_declining = 1.0 if left_end_v < left_start_v else 0.5
        vol_score = (vol_rising + vol_declining) / 2.0

    # Combine into confidence score
    raw = (curv_norm * 40 + slope_score * 30 + center_score * 20 + vol_score * 10)
    score[i] = min(100.0, max(0.0, raw))

    # Breakout: price crosses above the neckline (max of left rim and right recent)
    neckline = max(window[0], window[-1])
    if cl[i] > neckline and score[i] >= curvature_thresh:
        # Confirm it was below neckline recently
        if np.min(window[half-2:half+2]) < neckline * 0.98:
            breakout[i] = True

thresh_line = np.full(n, float(curvature_thresh))

plot(score.tolist(), title="Rounding Score", color="#26c6da", linewidth=2)
plot(thresh_line.tolist(), title="Threshold", color="#f44336", linewidth=1)
hline(0, title="Zero", color="#555555", linestyle="dashed")
bgcolor((score >= curvature_thresh).tolist(), color="rgba(76,175,80,0.08)")
plotshape(breakout.tolist(), title="Breakout", style="triangleup", location="belowbar", color="#00e676", size="small")
