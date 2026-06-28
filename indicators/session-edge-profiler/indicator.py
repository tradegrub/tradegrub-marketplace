from tg_scripting import *
import numpy as np

# --- Inputs ---
lookback = input.int(60, "Lookback Periods", minval=10, maxval=500)
session_mode = input.int(0, "Session Mode (0=Forex 1=Custom)", minval=0, maxval=1)
asian_start = input.int(0, "Asian Start Hour (UTC)", minval=0, maxval=23)
asian_end = input.int(8, "Asian End Hour (UTC)", minval=0, maxval=23)
london_start = input.int(8, "London Start Hour (UTC)", minval=0, maxval=23)
london_end = input.int(16, "London End Hour (UTC)", minval=0, maxval=23)
ny_start = input.int(13, "NY Start Hour (UTC)", minval=0, maxval=23)
ny_end = input.int(21, "NY End Hour (UTC)", minval=0, maxval=23)
zscore_thresh = input.float(1.5, "Z-Score Alert Threshold", minval=0.5, maxval=4.0)
show_percentiles = input.bool(True, "Show Percentile Rankings")
show_zscores = input.bool(True, "Show Z-Scores")

# --- Session Detection (vectorized) ---
n = len(close)
hours = np.arange(n) % 24  # simplified hour proxy from bar index

# Build session masks using vectorized conditionals
if session_mode == 0:
    asian_mask = np.where((hours >= asian_start) & (hours < asian_end), 1.0, 0.0)
    london_mask = np.where((hours >= london_start) & (hours < london_end), 1.0, 0.0)
    ny_mask = np.where((hours >= ny_start) & (hours < ny_end), 1.0, 0.0)
else:
    asian_mask = np.where((hours >= asian_start) & (hours < asian_end), 1.0, 0.0)
    london_mask = np.where((hours >= london_start) & (hours < london_end), 1.0, 0.0)
    ny_mask = np.where((hours >= ny_start) & (hours < ny_end), 1.0, 0.0)

# --- Per-Bar Range and Directional Metrics ---
bar_range = np.array(high) - np.array(low)
bar_direction = np.sign(np.array(close) - np.array(open))
bar_body = np.abs(np.array(close) - np.array(open))
bar_wick_ratio = np.where(bar_range > 0, bar_body / bar_range, 0.0)

# --- Rolling Window Statistics via stride_tricks ---
def rolling_windows(arr, window):
    """Create rolling window view of array without copies."""
    arr = np.asarray(arr, dtype=np.float64)
    if len(arr) < window:
        return np.array([]).reshape(0, window)
    shape = (len(arr) - window + 1, window)
    strides = (arr.strides[0], arr.strides[0])
    return np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)

def session_rolling_stats(data, mask, window):
    """Compute rolling mean, std, percentile for session-filtered data."""
    masked = data * mask
    masked_valid = np.where(mask > 0, data, np.nan)

    result_mean = np.full(n, np.nan)
    result_std = np.full(n, np.nan)
    result_p25 = np.full(n, np.nan)
    result_p50 = np.full(n, np.nan)
    result_p75 = np.full(n, np.nan)
    result_zscore = np.full(n, 0.0)
    result_winrate = np.full(n, 0.0)

    if n >= window:
        windows = rolling_windows(masked_valid, window)
        for i in range(windows.shape[0]):
            w = windows[i]
            valid = w[~np.isnan(w)]
            if len(valid) >= 3:
                idx = i + window - 1
                m = np.nanmean(valid)
                s = np.nanstd(valid)
                result_mean[idx] = m
                result_std[idx] = s
                result_p25[idx] = np.percentile(valid, 25)
                result_p50[idx] = np.percentile(valid, 50)
                result_p75[idx] = np.percentile(valid, 75)
                if s > 0:
                    result_zscore[idx] = (data[idx] - m) / s

    # Win rate: fraction of bars with positive direction in session
    dir_masked = np.where(mask > 0, bar_direction, np.nan)
    if n >= window:
        dir_wins = rolling_windows(dir_masked, window)
        for i in range(dir_wins.shape[0]):
            w = dir_wins[i]
            valid = w[~np.isnan(w)]
            if len(valid) > 0:
                idx = i + window - 1
                result_winrate[idx] = np.sum(valid > 0) / len(valid)

    return result_mean, result_std, result_p25, result_p50, result_p75, result_zscore, result_winrate

# --- Compute stats for each session ---
a_mean, a_std, a_p25, a_p50, a_p75, a_zscore, a_winrate = session_rolling_stats(bar_range, asian_mask, lookback)
l_mean, l_std, l_p25, l_p50, l_p75, l_zscore, l_winrate = session_rolling_stats(bar_range, london_mask, lookback)
ny_mean, ny_std, ny_p25, ny_p50, ny_p75, ny_zscore, ny_winrate = session_rolling_stats(bar_range, ny_mask, lookback)

# --- Session Range Ratios (London/Asian, NY/Asian) ---
range_ratio_la = np.where((a_mean is not None) & (a_mean > 0), l_mean / np.where(a_mean > 0, a_mean, 1.0), 1.0)
range_ratio_nya = np.where((a_mean is not None) & (a_mean > 0), ny_mean / np.where(a_mean > 0, a_mean, 1.0), 1.0)

# --- Histogram Distribution Analysis ---
def histogram_score(data, mask, current_val, bins=20):
    """Score current value against historical distribution using histogram."""
    valid = data[mask > 0]
    valid = valid[~np.isnan(valid)]
    if len(valid) < 10:
        return np.full(n, 0.5)
    hist_counts, bin_edges = np.histogram(valid, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    total = np.sum(hist_counts)
    cdf = np.cumsum(hist_counts).astype(np.float64) / total

    score = np.full(n, 0.5)
    for i in range(n):
        if not np.isnan(current_val[i]):
            idx = np.searchsorted(bin_edges[1:], current_val[i])
            idx = np.clip(idx, 0, len(cdf) - 1)
            score[i] = cdf[idx]
    return score

hist_score_asian = histogram_score(bar_range, asian_mask, bar_range)
hist_score_london = histogram_score(bar_range, london_mask, bar_range)
hist_score_ny = histogram_score(bar_range, ny_mask, bar_range)

# --- Composite Session Edge Score ---
# Combines z-score magnitude, percentile rank, and wick ratio for edge detection
asian_edge = np.clip(np.abs(a_zscore) * hist_score_asian * (1 + bar_wick_ratio), 0, 5)
london_edge = np.clip(np.abs(l_zscore) * hist_score_london * (1 + bar_wick_ratio), 0, 5)
ny_edge = np.clip(np.abs(ny_zscore) * hist_score_ny * (1 + bar_wick_ratio), 0, 5)

# --- Alerts: z-score exceeds threshold ---
asian_alert = np.where(np.abs(a_zscore) > zscore_thresh, a_zscore, 0.0)
london_alert = np.where(np.abs(l_zscore) > zscore_thresh, l_zscore, 0.0)
ny_alert = np.where(np.abs(ny_zscore) > zscore_thresh, ny_zscore, 0.0)

# --- Plotting ---
p_ae = plot(asian_edge, title="Asian Edge", color="#FF9800")
p_le = plot(london_edge, title="London Edge", color="#2196F3")
p_ne = plot(ny_edge, title="NY Edge", color="#4CAF50")

if show_percentiles:
    plot(a_p50, title="Asian Median Range", color="rgba(255,152,0,0.4)")
    plot(l_p50, title="London Median Range", color="rgba(33,150,243,0.4)")
    plot(ny_p50, title="NY Median Range", color="rgba(76,175,80,0.4)")

if show_zscores:
    plot(a_zscore, title="Asian Z-Score", color="#FFC107")
    plot(l_zscore, title="London Z-Score", color="#03A9F4")
    plot(ny_zscore, title="NY Z-Score", color="#8BC34A")

plot(a_winrate * 100, title="Asian Win Rate %", color="rgba(255,152,0,0.6)")
plot(l_winrate * 100, title="London Win Rate %", color="rgba(33,150,243,0.6)")
plot(ny_winrate * 100, title="NY Win Rate %", color="rgba(76,175,80,0.6)")

plot(range_ratio_la, title="London/Asian Range Ratio", color="#9C27B0")
plot(range_ratio_nya, title="NY/Asian Range Ratio", color="#E91E63")

hline(zscore_thresh, title="Z-Score Upper", color="red")
hline(-zscore_thresh, title="Z-Score Lower", color="red")
hline(0, title="Zero", color="gray")

# Background highlight on extreme z-scores
bgcolor(np.abs(a_zscore) > zscore_thresh, color="rgba(255,152,0,0.1)")
bgcolor(np.abs(l_zscore) > zscore_thresh, color="rgba(33,150,243,0.1)")
bgcolor(np.abs(ny_zscore) > zscore_thresh, color="rgba(76,175,80,0.1)")
