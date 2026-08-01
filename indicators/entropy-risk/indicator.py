from tg_scripting import *
import numpy as np
from scipy.stats import entropy as sp_entropy
from scipy.stats import norm

indicator("Entropy Risk Measurement", overlay=False)

lookback = input.int(50, "Lookback Period", minval=20, maxval=200)
num_bins = input.int(20, "Distribution Bins", minval=5, maxval=50)
high_entropy = input.float(2.5, "High Entropy Threshold", minval=1.0, maxval=4.0)
low_entropy = input.float(1.5, "Low Entropy Threshold", minval=0.5, maxval=3.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")
label_cooldown = input.int(20, "Label Cooldown Bars", minval=5, maxval=50)

close_arr = np.array(close, dtype=np.float64)
n = len(close_arr)

# Compute log returns
log_returns = np.zeros(n)
for i in range(1, n):
    if close_arr[i - 1] > 0:
        log_returns[i] = np.log(close_arr[i] / close_arr[i - 1])

# Rolling metrics
shannon_entropy = np.full(n, np.nan)
kl_divergence = np.full(n, np.nan)
surprise_factor = np.full(n, np.nan)

for i in range(lookback, n):
    window = log_returns[i - lookback + 1:i + 1]

    # Shannon entropy of return distribution
    hist_counts, bin_edges = np.histogram(window, bins=num_bins, density=False)
    probs = hist_counts / hist_counts.sum()
    probs = probs[probs > 0]  # Remove zero bins
    h = float(sp_entropy(probs, base=2))
    shannon_entropy[i] = h

    # KL divergence from normal distribution
    mu = np.mean(window)
    sigma = np.std(window)
    if sigma > 1e-10:
        hist_density, _ = np.histogram(window, bins=num_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        bin_width = bin_edges[1] - bin_edges[0]

        # Normal reference distribution
        normal_density = norm.pdf(bin_centers, loc=mu, scale=sigma)
        normal_probs = normal_density * bin_width
        normal_probs = normal_probs / normal_probs.sum()

        empirical_probs = hist_density * bin_width
        empirical_probs = empirical_probs / empirical_probs.sum()

        # Add small epsilon to avoid log(0)
        eps = 1e-10
        empirical_probs = empirical_probs + eps
        normal_probs = normal_probs + eps
        empirical_probs = empirical_probs / empirical_probs.sum()
        normal_probs = normal_probs / normal_probs.sum()

        kl = float(sp_entropy(empirical_probs, normal_probs, base=2))
        kl_divergence[i] = kl
    else:
        kl_divergence[i] = 0.0

    # Surprise factor: how unlikely is the current return
    curr_ret = log_returns[i]
    if sigma > 1e-10:
        z = abs(curr_ret - mu) / sigma
        surprise_factor[i] = z
    else:
        surprise_factor[i] = 0.0

# Plots
plot(shannon_entropy, title="Shannon Entropy", color="#42A5F5")
plot(kl_divergence, title="KL Divergence", color="#FF7043")
plot(surprise_factor, title="Surprise Factor", color="#AB47BC")

if show_levels:
    hline(float(high_entropy), title="High Entropy", color="rgba(239,83,80,0.5)")
    hline(float(low_entropy), title="Low Entropy", color="rgba(76,175,80,0.5)")
    hline(2.0, title="Surprise 2σ", color="rgba(171,71,188,0.4)")

# Risk zones
high_risk = (shannon_entropy > high_entropy) & (~np.isnan(shannon_entropy))
low_risk = (shannon_entropy < low_entropy) & (~np.isnan(shannon_entropy))

bgcolor(high_risk, color="rgba(239,83,80,0.08)")
bgcolor(low_risk, color="rgba(76,175,80,0.06)")

# Surprise spikes
surprise_spike = (surprise_factor > 2.5) & (~np.isnan(surprise_factor))
bgcolor(surprise_spike, color="rgba(171,71,188,0.08)")

if show_labels:
    last_high = -label_cooldown
    last_low = -label_cooldown
    last_surprise = -label_cooldown

    for i in range(lookback, n):
        if high_risk[i] and (i - last_high) > label_cooldown:
            label.new(
                x=i, y=float(shannon_entropy[i]),
                text=f"High Risk\nH={shannon_entropy[i]:.2f}",
                style=label.style_label_down,
                color="rgba(239,83,80,0.3)",
                textcolor="#ef5350",
                size="small"
            )
            last_high = i

        if low_risk[i] and (i - last_low) > label_cooldown:
            label.new(
                x=i, y=float(shannon_entropy[i]),
                text=f"Low Risk\nH={shannon_entropy[i]:.2f}",
                style=label.style_label_up,
                color="rgba(76,175,80,0.3)",
                textcolor="#4CAF50",
                size="small"
            )
            last_low = i

        if surprise_spike[i] and (i - last_surprise) > label_cooldown:
            label.new(
                x=i, y=float(surprise_factor[i]),
                text=f"Surprise\n{surprise_factor[i]:.1f}σ",
                style=label.style_label_down,
                color="rgba(171,71,188,0.3)",
                textcolor="#AB47BC",
                size="small"
            )
            last_surprise = i

# Current status
if n > lookback and not np.isnan(shannon_entropy[-1]):
    h_val = float(shannon_entropy[-1])
    kl_val = float(kl_divergence[-1]) if not np.isnan(kl_divergence[-1]) else 0.0
    s_val = float(surprise_factor[-1]) if not np.isnan(surprise_factor[-1]) else 0.0
    label.new(
        x=n - 1, y=h_val,
        text=f"H: {h_val:.2f} | KL: {kl_val:.3f} | S: {s_val:.1f}σ",
        style=label.style_label_left,
        color="rgba(66,165,245,0.3)",
        textcolor="#42A5F5",
        size="normal"
    )
