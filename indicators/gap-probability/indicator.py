from tg_scripting import *
import numpy as np

indicator("Movement Probability", overlay=False)

ma_length = input.int(20, "MA Length", minval=5, maxval=100)
lookback = input.int(200, "Lookback", minval=50, maxval=500)

src = np.array(close, dtype=float)
n = len(src)

sma_vals = np.array(ta.sma(close, ma_length), dtype=float)

up_prob = np.full(n, 50.0)
down_prob = np.full(n, 50.0)

if n > lookback + ma_length:
    std_arr = np.zeros(n)
    for i in range(ma_length, n):
        window = src[i - ma_length:i]
        std_arr[i] = float(np.std(window))

    zscore = np.where(std_arr > 0, (src - sma_vals) / std_arr, 0.0)
    zscore = np.nan_to_num(zscore, nan=0.0)

    z_bins = np.linspace(-3.0, 3.0, 13)

    for i in range(lookback + 1, n):
        hist_start = i - lookback
        current_z = zscore[i]

        bin_idx = int(np.digitize(current_z, z_bins)) - 1
        bin_idx = max(0, min(bin_idx, len(z_bins) - 2))

        low_z = z_bins[bin_idx]
        high_z = z_bins[min(bin_idx + 1, len(z_bins) - 1)]

        similar_mask = (zscore[hist_start:i] >= low_z) & (zscore[hist_start:i] <= high_z)
        similar_indices = np.where(similar_mask)[0] + hist_start

        if len(similar_indices) > 5:
            next_indices = similar_indices[similar_indices < i - 1] + 1
            valid = next_indices[next_indices < i]

            if len(valid) > 3:
                moves = src[valid] - src[valid - 1]
                up_count = float(np.sum(moves > 0))
                total = float(len(moves))
                up_prob[i] = up_count / total * 100
                down_prob[i] = (1.0 - up_count / total) * 100

plot(up_prob.tolist(), title="Up Probability", color="#4CAF50", linewidth=2)
plot(down_prob.tolist(), title="Down Probability", color="#f44336", linewidth=2)
hline(50, title="Neutral", color="#555555", linestyle="dashed")
hline(65, title="High Probability", color="#FF9800", linestyle="dashed")
