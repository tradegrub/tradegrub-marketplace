from tg_scripting import *
import numpy as np

indicator("Consolidation Quality", overlay=False)

length = input.int(20, "Lookback Length", minval=5, maxval=100)
vol_length = input.int(20, "Volume MA Length", minval=5, maxval=100)
ma_fast = input.int(10, "Fast MA", minval=5, maxval=50)
ma_slow = input.int(30, "Slow MA", minval=10, maxval=100)
range_wt = input.float(0.4, "Range Weight", minval=0.0, maxval=1.0)
vol_wt = input.float(0.3, "Volume Weight", minval=0.0, maxval=1.0)
ma_wt = input.float(0.3, "MA Convergence Weight", minval=0.0, maxval=1.0)
threshold = input.float(70.0, "Quality Threshold", minval=0.0, maxval=100.0)
show_bg = input.bool(True, "Highlight Quality Zones")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

highest_high = ta.highest(high, length)
lowest_low = ta.lowest(low, length)
current_range = highest_high - lowest_low
prev_high = np.roll(highest_high, length)
prev_high[:length] = np.nan
prev_low = np.roll(lowest_low, length)
prev_low[:length] = np.nan
prev_range = prev_high - prev_low
range_contraction = np.where(prev_range > 0, (1 - current_range / prev_range) * 100, 0)
range_score = np.clip(range_contraction, 0, 100)

vol_ma = ta.sma(volume, vol_length)
vol_ratio = np.where(vol_ma > 0, volume / vol_ma, 1.0)
vol_decline = (1 - np.clip(vol_ratio, 0, 2) / 2) * 100
vol_score = np.clip(vol_decline, 0, 100)

ema_fast = ta.ema(close, ma_fast)
ema_slow = ta.ema(close, ma_slow)
ma_spread = np.abs(ema_fast - ema_slow)
ma_spread_pct = np.where(ema_slow > 0, ma_spread / ema_slow * 100, 0)
ma_norm = ta.highest(ma_spread_pct, length)
convergence = np.where(ma_norm > 0, (1 - ma_spread_pct / ma_norm) * 100, 0)
ma_score = np.clip(convergence, 0, 100)

total_wt = range_wt + vol_wt + ma_wt
quality = (range_score * range_wt + vol_score * vol_wt + ma_score * ma_wt) / total_wt

smoothed = ta.sma(quality, 3)

plot(smoothed, title="Quality Score", color="teal", linewidth=2)
hline(threshold, title="Threshold", color="gray", linestyle="dashed")
hline(80, title="High Quality", color="green", linestyle="dotted")
hline(30, title="Low Quality", color="red", linestyle="dotted")

if show_bg:
    bgcolor(smoothed >= threshold, color="rgba(0,128,128,0.1)")

# --- Rich annotations ---
n = len(close)
last_high_idx = -100
last_low_idx = -100
last_entry_idx = -100
cooldown = 20

for i in range(length, n):
    if show_labels:
        # High quality consolidation zone
        if smoothed[i] >= 80 and (i - last_high_idx) > cooldown:
            label.new(
                x=i, y=float(smoothed[i]),
                text="Tight Base",
                style=label.style_label_down,
                color="rgba(0,230,118,0.2)",
                textcolor="#00e676",
                size="small"
            )
            last_high_idx = i

        # Low quality / choppy
        if smoothed[i] <= 30 and (i - last_low_idx) > cooldown:
            label.new(
                x=i, y=float(smoothed[i]),
                text="Choppy",
                style=label.style_label_up,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_low_idx = i

    if show_levels:
        # Breakout from consolidation: quality drops from above threshold to below
        if i > length and smoothed[i - 1] >= threshold and smoothed[i] < threshold and (i - last_entry_idx) > cooldown:
            label.new(
                x=i, y=float(smoothed[i]),
                text="Breakout",
                style=label.style_label_up,
                color="rgba(66,165,245,0.2)",
                textcolor="#42a5f5",
                size="small"
            )
            last_entry_idx = i
