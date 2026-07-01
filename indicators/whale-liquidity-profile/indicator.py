from tg_scripting import *
import numpy as np

indicator("Whale Liquidity Profile", overlay=True)

# --- Inputs ---
vol_lookback = input.int(50, "Volume Lookback", minval=10, maxval=200)
whale_percentile = input.float(85.0, "Whale Percentile", minval=50.0, maxval=99.0)
absorption_threshold = input.float(2.0, "Absorption Ratio Threshold", minval=0.5, maxval=10.0)
profile_bins = input.int(20, "Profile Bins", minval=5, maxval=100)
show_absorption = input.bool(True, "Show Absorption Zones")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)

# --- Rolling percentile whale detection ---
# Classify each bar's volume as whale or retail based on rolling percentile
whale_mask = np.zeros(n, dtype=bool)
whale_volume = np.zeros(n)
retail_volume = np.zeros(n)

for i in range(vol_lookback, n):
    window = volume[i - vol_lookback:i]
    threshold = np.percentile(window, whale_percentile)
    if volume[i] >= threshold:
        whale_mask[i] = True
        whale_volume[i] = volume[i]
    else:
        retail_volume[i] = volume[i]

# --- Absorption detection ---
# Absorption = large volume with minimal price movement (institutional accumulation/distribution)
price_range = high - low
price_range_safe = np.where(price_range < 1e-8, 1e-8, price_range)
absorption_ratio = volume / price_range_safe

# Normalize absorption ratio relative to its rolling mean
absorption_mean = ta.sma(absorption_ratio, vol_lookback)
absorption_std = ta.stdev(absorption_ratio, vol_lookback)
absorption_std_safe = np.where(absorption_std < 1e-8, 1e-8, absorption_std)
absorption_z = (absorption_ratio - absorption_mean) / absorption_std_safe

# Absorption zones: high volume, low price movement
is_absorption = absorption_z > absorption_threshold

# --- Volume-at-price horizontal profile ---
# Build histogram of whale volume across price levels
price_min = np.nanmin(low)
price_max = np.nanmax(high)
bin_edges = np.linspace(price_min, price_max, profile_bins + 1)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

# Assign each bar's typical price to a bin and accumulate whale volume
typical_price = (high + low + close) / 3.0
whale_profile = np.zeros(profile_bins)
retail_profile = np.zeros(profile_bins)

bin_indices = np.clip(
    np.digitize(typical_price, bin_edges) - 1, 0, profile_bins - 1
)
for i in range(n):
    b = bin_indices[i]
    if whale_mask[i]:
        whale_profile[b] += volume[i]
    else:
        retail_profile[b] += volume[i]

# --- Map dominant whale level back to price series ---
# Find the bin with highest whale accumulation
peak_whale_bin = np.argmax(whale_profile)
whale_support_price = np.full(n, bin_centers[peak_whale_bin])

# Secondary whale level
whale_profile_copy = whale_profile.copy()
whale_profile_copy[peak_whale_bin] = 0
secondary_bin = np.argmax(whale_profile_copy)
whale_secondary_price = np.full(n, bin_centers[secondary_bin])

# --- Cumulative whale delta (buying pressure vs selling pressure) ---
# Positive delta = whale buying (close > open), negative = whale selling
whale_direction = np.where(close > open, 1.0, -1.0)
whale_delta = np.where(whale_mask, whale_volume * whale_direction, 0.0)
cumulative_whale_delta = np.cumsum(whale_delta)

# Normalize to plot scale
delta_range = np.nanmax(np.abs(cumulative_whale_delta)) or 1.0
norm_delta = (cumulative_whale_delta / delta_range) * (price_max - price_min) * 0.1 + np.nanmean(close)

# --- Whale intensity (smoothed percentage of whale bars) ---
whale_float = whale_mask.astype(float)
whale_intensity = ta.sma(whale_float, vol_lookback) * 100.0

# --- Plotting ---
plot(whale_support_price, title="Primary Whale Level", color="#1565C0")
plot(whale_secondary_price, title="Secondary Whale Level", color="#42A5F5")
plot(norm_delta, title="Cumulative Whale Delta", color="#AB47BC")

# Background color for absorption zones
if show_absorption:
    bgcolor(is_absorption, color="rgba(255, 183, 77, 0.2)")

# Mark whale bars
plotshape(whale_mask, title="Whale Bar", style="triangleup", location="belowbar", color="#1565C0", size="small")

# Mark absorption events (whale + absorption)
absorption_events = np.logical_and(whale_mask, is_absorption)
plotshape(absorption_events, title="Absorption", style="diamond", location="abovebar", color="#FF6F00", size="small")

# --- Rich annotations ---
last_whale_label_idx = -100
last_absorption_label_idx = -100
last_level_label_idx = -100
label_cooldown = vol_lookback

for i in range(vol_lookback, n):
    # Label whale bars with high volume
    if show_labels and whale_mask[i] and (i - last_whale_label_idx) > label_cooldown:
        last_whale_label_idx = i
        direction = "Whale Buy" if close[i] > open[i] else "Whale Sell"
        c = "#00e676" if close[i] > open[i] else "#ef5350"
        label.new(
            x=i, y=float(low[i]),
            text=direction,
            style=label.style_label_up,
            color=f"rgba({66 if close[i] > open[i] else 239},{165 if close[i] > open[i] else 83},{245 if close[i] > open[i] else 80},0.25)",
            textcolor=c,
            size="small"
        )

    # Label absorption events
    if show_labels and absorption_events[i] and (i - last_absorption_label_idx) > label_cooldown:
        last_absorption_label_idx = i
        label.new(
            x=i, y=float(high[i]),
            text="Absorption",
            style=label.style_label_down,
            color="rgba(255,111,0,0.25)",
            textcolor="#FF6F00",
            size="small"
        )
        if show_levels:
            end_bar = min(i + vol_lookback, n - 1)
            box.new(left=i, top=float(high[i]), right=end_bar, bottom=float(low[i]),
                    border_color="rgba(255,183,77,0.2)", bgcolor="rgba(255,183,77,0.03)")

# Label primary and secondary whale levels once
if show_levels and n > vol_lookback:
    mid_bar = n // 2
    label.new(
        x=mid_bar, y=float(whale_support_price[0]),
        text="Primary Whale Level",
        style=label.style_label_left,
        color="rgba(21,101,192,0.25)",
        textcolor="#1565C0",
        size="small"
    )
    label.new(
        x=mid_bar + 20, y=float(whale_secondary_price[0]),
        text="Secondary Whale Level",
        style=label.style_label_left,
        color="rgba(66,165,245,0.25)",
        textcolor="#42A5F5",
        size="small"
    )
