from tg_scripting import *
import numpy as np

indicator("Walk-Forward Efficiency", overlay=False)

in_sample_len = input.int(60, "In-Sample Length", minval=20, maxval=200)
out_sample_len = input.int(20, "Out-of-Sample Length", minval=10, maxval=100)
num_windows = input.int(5, "Number of Windows", minval=2, maxval=10)

src = np.array(close, dtype=float)
n = len(src)

segment_len = in_sample_len + out_sample_len
total_lookback = segment_len * num_windows


def lin_reg_r2(y):
    m = len(y)
    if m < 3:
        return 0.0
    x = np.arange(m, dtype=float)
    x_mean = x.mean()
    y_mean = y.mean()
    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    ss_xx = np.sum((x - x_mean) ** 2)
    if ss_xx == 0:
        return 0.0
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    if ss_tot == 0:
        return 0.0
    return max(0.0, 1.0 - ss_res / ss_tot)


def predict_r2(in_data, out_data):
    n_in = len(in_data)
    x_in = np.arange(n_in, dtype=float)
    x_mean = x_in.mean()
    y_mean = in_data.mean()
    ss_xy = np.sum((x_in - x_mean) * (in_data - y_mean))
    ss_xx = np.sum((x_in - x_mean) ** 2)
    if ss_xx == 0:
        return 0.0
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    n_out = len(out_data)
    x_out = np.arange(n_in, n_in + n_out, dtype=float)
    y_pred = slope * x_out + intercept
    ss_res = np.sum((out_data - y_pred) ** 2)
    out_mean = out_data.mean()
    ss_tot = np.sum((out_data - out_mean) ** 2)
    if ss_tot == 0:
        return 0.0
    return max(0.0, 1.0 - ss_res / ss_tot)


wfe_values = np.full(n, np.nan)

for i in range(total_lookback, n):
    efficiencies = []
    for w in range(num_windows):
        offset = w * segment_len
        start = i - total_lookback + offset
        in_end = start + in_sample_len
        out_end = in_end + out_sample_len

        in_data = src[start:in_end]
        out_data = src[in_end:out_end]

        in_r2 = lin_reg_r2(in_data)
        if in_r2 < 0.01:
            continue

        out_r2 = predict_r2(in_data, out_data)
        eff = min(100.0, max(0.0, (out_r2 / in_r2) * 100.0))
        efficiencies.append(eff)

    if len(efficiencies) > 0:
        wfe_values[i] = np.mean(efficiencies)
    else:
        wfe_values[i] = 0.0

plot(wfe_values.tolist(), title="WFE", color="#00BCD4", linewidth=2)

hline(75, title="Strong", color="#4CAF50", linestyle="dashed")
hline(50, title="Moderate", color="#FFA726", linestyle="dotted")
hline(25, title="Weak", color="#EF5350", linestyle="dotted")

bgcolor(wfe_values >= 75, color="rgba(76,175,80,0.08)")
bgcolor(wfe_values <= 25, color="rgba(239,83,80,0.08)")
