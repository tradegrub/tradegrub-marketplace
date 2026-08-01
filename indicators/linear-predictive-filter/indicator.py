from tg_scripting import *
import numpy as np

indicator("Linear Predictive Filter", overlay=False)

order = input.int(10, "LPC Order", minval=4, maxval=30)
lookback = input.int(100, "Lookback", minval=50, maxval=300)

src = np.array(close, dtype=float)
n = len(src)

predicted = np.full(n, np.nan)
cycle_length = np.full(n, np.nan)

for i in range(lookback, n):
    window = src[i - lookback:i]
    # Normalize
    mean_w = np.mean(window)
    std_w = np.std(window)
    if std_w < 1e-10:
        continue
    x = (window - mean_w) / std_w

    # Compute autocorrelation
    acf = np.correlate(x, x, mode="full")
    acf = acf[len(x) - 1:]
    acf = acf / acf[0]

    # Yule-Walker: solve R * a = r
    if order >= len(acf):
        continue
    r_vec = acf[1:order + 1]
    R_mat = np.zeros((order, order))
    for row in range(order):
        for col in range(order):
            idx = abs(row - col)
            if idx < len(acf):
                R_mat[row, col] = acf[idx]

    try:
        lpc_coeffs = np.linalg.solve(R_mat, r_vec)
    except np.linalg.LinAlgError:
        continue

    # Predict next value
    recent = x[-order:][::-1]
    pred_norm = np.dot(lpc_coeffs, recent)
    predicted[i] = pred_norm * std_w + mean_w

    # Find dominant cycle from LPC coefficients
    # Build polynomial: 1 - a1*z^-1 - a2*z^-2 - ...
    poly = np.zeros(order + 1)
    poly[0] = 1.0
    poly[1:] = -lpc_coeffs
    roots = np.roots(poly)

    # Find dominant frequency from roots inside unit circle
    valid = roots[np.abs(roots) < 1.0]
    if len(valid) > 0:
        angles = np.abs(np.angle(valid))
        angles = angles[angles > 0.01]  # filter near-zero
        if len(angles) > 0:
            # Dominant = smallest angle (longest cycle)
            dominant_angle = np.min(angles)
            cycle_length[i] = 2.0 * np.pi / dominant_angle

plot(predicted.tolist(), title="LPC Predicted Price", color="#26c6da", linewidth=2)
plot(cycle_length.tolist(), title="Dominant Cycle Length", color="#ff9800")
hline(0, title="Zero", color="#555555")
