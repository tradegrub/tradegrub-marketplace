from tg_scripting import *
import numpy as np

indicator("Kalman Filter Trend", overlay=True)

# --- Inputs ---
process_noise = input.float(0.01, "Process Noise (Q)", minval=0.0001, maxval=1.0)
measurement_noise = input.float(1.0, "Measurement Noise (R)", minval=0.01, maxval=50.0)
confidence_mult = input.float(2.0, "Confidence Band Multiplier", minval=0.5, maxval=5.0)
use_velocity = input.bool(True, "Include Velocity State")
adaptive = input.bool(True, "Adaptive Noise Estimation")
adaptive_window = input.int(20, "Adaptive Window", minval=5, maxval=100)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)

# --- Kalman Filter Implementation ---
# State vector: [price, velocity] if use_velocity, else [price]
# This is a full predict-update Kalman filter with matrix math

if use_velocity:
    # State transition matrix F (constant velocity model)
    F = np.array([[1.0, 1.0],
                  [0.0, 1.0]])
    # Measurement matrix H
    H = np.array([[1.0, 0.0]])
    # Process noise covariance Q
    Q = np.array([[process_noise, 0.0],
                  [0.0, process_noise * 0.1]])
    # Initial state
    x = np.array([close[0], 0.0])
    # Initial covariance
    P = np.eye(2) * 1.0
    dim = 2
else:
    F = np.array([[1.0]])
    H = np.array([[1.0]])
    Q = np.array([[process_noise]])
    x = np.array([close[0]])
    P = np.array([[1.0]])
    dim = 1

R = np.array([[measurement_noise]])

# Output arrays
filtered_price = np.zeros(n)
upper_band = np.zeros(n)
lower_band = np.zeros(n)
kalman_gain_series = np.zeros(n)
innovation_series = np.zeros(n)
velocity_series = np.zeros(n)

for i in range(n):
    # === PREDICT STEP ===
    # State prediction: x_pred = F * x
    x_pred = np.dot(F, x)
    # Covariance prediction: P_pred = F * P * F^T + Q
    P_pred = np.dot(np.dot(F, P), F.T) + Q

    # === ADAPTIVE NOISE ESTIMATION ===
    # Dynamically adjust R based on recent prediction errors
    if adaptive and i >= adaptive_window:
        recent_innovations = innovation_series[i - adaptive_window:i]
        innovation_var = np.var(recent_innovations)
        # Innovation covariance should equal H*P_pred*H^T + R
        # So R_adaptive = innovation_var - H*P_pred*H^T
        predicted_var = np.dot(np.dot(H, P_pred), H.T)[0, 0]
        R_adaptive = np.array([[max(0.01, innovation_var - predicted_var)]])
    else:
        R_adaptive = R

    # === UPDATE STEP ===
    # Innovation (measurement residual): y = z - H * x_pred
    z = close[i]
    y = z - np.dot(H, x_pred)[0]
    innovation_series[i] = y

    # Innovation covariance: S = H * P_pred * H^T + R
    S = np.dot(np.dot(H, P_pred), H.T) + R_adaptive
    S_inv = np.linalg.inv(S)

    # Kalman gain: K = P_pred * H^T * S^-1
    K = np.dot(np.dot(P_pred, H.T), S_inv)

    # State update: x = x_pred + K * y
    x = x_pred + K.flatten() * y

    # Covariance update: P = (I - K * H) * P_pred
    # Joseph form for numerical stability: P = (I-KH)*P_pred*(I-KH)^T + K*R*K^T
    IKH = np.eye(dim) - np.dot(K, H)
    P = np.dot(np.dot(IKH, P_pred), IKH.T) + np.dot(np.dot(K, R_adaptive), K.T)

    # Store outputs
    filtered_price[i] = x[0]
    if use_velocity:
        velocity_series[i] = x[1]

    # Confidence bands from state covariance
    state_uncertainty = np.sqrt(P[0, 0])
    upper_band[i] = x[0] + confidence_mult * state_uncertainty
    lower_band[i] = x[0] - confidence_mult * state_uncertainty

    # Track Kalman gain magnitude
    kalman_gain_series[i] = K[0, 0]

# --- Trend direction from filtered price ---
filtered_change = np.diff(filtered_price, prepend=filtered_price[0])
trend_up = filtered_change > 0
trend_down = filtered_change < 0

# Color the filtered line by trend direction
trend_color = np.where(trend_up, "#26A69A", "#EF5350")

# --- Normalized Kalman gain for subplot ---
kg_min = np.nanmin(kalman_gain_series[adaptive_window:])
kg_max = np.nanmax(kalman_gain_series[adaptive_window:])
kg_range = kg_max - kg_min if kg_max > kg_min else 1.0
kalman_gain_norm = (kalman_gain_series - kg_min) / kg_range * 100.0

# --- Plotting ---
p1 = plot(upper_band, title="Upper Confidence", color="rgba(38, 166, 154, 0.3)")
p2 = plot(filtered_price, title="Kalman Filtered Price", color="#1565C0")
p3 = plot(lower_band, title="Lower Confidence", color="rgba(239, 83, 80, 0.3)")

fill(p1, p3, color="rgba(21, 101, 192, 0.08)")

# Trend reversal signals
trend_bull = np.logical_and(trend_up, np.roll(trend_down, 1))
trend_bear = np.logical_and(trend_down, np.roll(trend_up, 1))
plotshape(trend_bull, title="Bull Reversal", style="triangleup", location="belowbar", color="#26A69A", size="small")
plotshape(trend_bear, title="Bear Reversal", style="triangledown", location="abovebar", color="#EF5350", size="small")

# --- Rich annotations ---
last_bull_idx = -100
last_bear_idx = -100
last_band_idx = -100
cooldown = 20

for i in range(adaptive_window, n):
    if show_labels:
        # Trend flip to bullish
        if trend_bull[i] and (i - last_bull_idx) > cooldown:
            label.new(
                x=i, y=float(low[i]),
                text="Trend Up",
                style=label.style_label_up,
                color="rgba(38,166,154,0.2)",
                textcolor="#26A69A",
                size="small"
            )
            last_bull_idx = i

        # Trend flip to bearish
        if trend_bear[i] and (i - last_bear_idx) > cooldown:
            label.new(
                x=i, y=float(high[i]),
                text="Trend Down",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#EF5350",
                size="small"
            )
            last_bear_idx = i

    if show_levels:
        # Price breaking outside confidence bands
        if close[i] > upper_band[i] and (i - last_band_idx) > cooldown:
            label.new(
                x=i, y=float(upper_band[i]),
                text="Above Band",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#00e676",
                size="tiny"
            )
            last_band_idx = i
        elif close[i] < lower_band[i] and (i - last_band_idx) > cooldown:
            label.new(
                x=i, y=float(lower_band[i]),
                text="Below Band",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#ef5350",
                size="tiny"
            )
            last_band_idx = i
