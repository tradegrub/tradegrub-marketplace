from tg_scripting import *
import numpy as np
from matplotlib import pyplot as plt

indicator("Price Distribution Analysis", overlay=False)

lookback = input.int(100, "Lookback Period", minval=20, maxval=500)
num_bins = input.int(20, "Number of Bins", minval=5, maxval=50)
zscore_warn = input.float(2.0, "Z-Score Warning Level", minval=0.5, maxval=4.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)

percentile_rank = np.full(n, np.nan)
zscore = np.full(n, np.nan)
bin_density = np.full(n, np.nan)

for i in range(lookback, n):
    window = close[i - lookback:i + 1]
    price = close[i]

    hist_counts, bin_edges = np.histogram(window, bins=num_bins, density=True)

    bin_idx = np.searchsorted(bin_edges[1:], price)
    bin_idx = min(bin_idx, len(hist_counts) - 1)
    bin_density[i] = float(hist_counts[bin_idx])

    mean_val = np.mean(window)
    std_val = np.std(window)
    if std_val > 0:
        zscore[i] = float((price - mean_val) / std_val)
    else:
        zscore[i] = 0.0

    percentile_rank[i] = float(np.sum(window <= price) / len(window) * 100)

plot(zscore, title="Z-Score", color="#42A5F5")
plot(percentile_rank, title="Percentile Rank", color="#AB47BC")
plot(bin_density, title="Bin Density", color="#66BB6A")

if show_levels:
    hline(0, title="Z-Score Zero", color="rgba(255,255,255,0.3)")
    hline(float(zscore_warn), title="Upper Warning", color="rgba(239,83,80,0.5)")
    hline(float(-zscore_warn), title="Lower Warning", color="rgba(76,175,80,0.5)")
    hline(50, title="Median Percentile", color="rgba(255,255,255,0.2)")

overbought = (zscore > zscore_warn) & (~np.isnan(zscore))
oversold = (zscore < -zscore_warn) & (~np.isnan(zscore))

bgcolor(overbought, color="rgba(239,83,80,0.08)")
bgcolor(oversold, color="rgba(76,175,80,0.08)")

if show_labels:
    last_ob_idx = -100
    last_os_idx = -100
    cooldown = 20

    for i in range(lookback, n):
        if overbought[i] and (i - last_ob_idx) > cooldown:
            label.new(
                x=i, y=float(zscore[i]),
                text=f"OB z={zscore[i]:.1f}\nP{percentile_rank[i]:.0f}",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_ob_idx = i

        if oversold[i] and (i - last_os_idx) > cooldown:
            label.new(
                x=i, y=float(zscore[i]),
                text=f"OS z={zscore[i]:.1f}\nP{percentile_rank[i]:.0f}",
                style=label.style_label_up,
                color="rgba(76,175,80,0.2)",
                textcolor="#4CAF50",
                size="small"
            )
            last_os_idx = i

if n > lookback and not np.isnan(zscore[-1]):
    curr_z = float(zscore[-1])
    curr_p = float(percentile_rank[-1])
    curr_d = float(bin_density[-1])
    label.new(
        x=n - 1, y=curr_z,
        text=f"Z: {curr_z:.2f} | P: {curr_p:.0f}% | D: {curr_d:.2f}",
        style=label.style_label_left,
        color="rgba(66,165,245,0.3)",
        textcolor="#42A5F5",
        size="normal"
    )
