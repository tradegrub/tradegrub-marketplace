from tg_scripting import *
import numpy as np

indicator("ATR Percent", overlay=False)

length = input.int(14, "ATR Length", minval=1, maxval=100)
smooth = input.int(5, "Smoothing", minval=1, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

atr_val = ta.atr(high, low, close, length)
atr_pct = (atr_val / close) * 100
atr_pct_smooth = ta.sma(atr_pct, smooth)

plot(atr_pct, title="ATR %", color="#AB47BC")
plot(atr_pct_smooth, title="Smoothed", color="#FF7043")

# --- Rich annotations ---
n = len(close)
last_high_vol_idx = -100
last_low_vol_idx = -100
cooldown = 20

# Compute thresholds for high/low volatility
atr_pct_mean = np.nanmean(atr_pct[length:])
atr_pct_std = np.nanstd(atr_pct[length:])
high_vol_level = atr_pct_mean + atr_pct_std
low_vol_level = max(atr_pct_mean - atr_pct_std, 0.01)

for i in range(length, n):
    if show_labels:
        # High volatility spike
        if atr_pct[i] > high_vol_level and (i - last_high_vol_idx) > cooldown:
            label.new(
                x=i, y=float(atr_pct[i]),
                text="High Vol",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_high_vol_idx = i

        # Low volatility (squeeze)
        if atr_pct[i] < low_vol_level and (i - last_low_vol_idx) > cooldown:
            label.new(
                x=i, y=float(atr_pct[i]),
                text="Squeeze",
                style=label.style_label_up,
                color="rgba(0,230,118,0.2)",
                textcolor="#00e676",
                size="small"
            )
            last_low_vol_idx = i

    if show_levels:
        # Crossover: ATR% crosses above smoothed (volatility expanding)
        if i > length and atr_pct[i] > atr_pct_smooth[i] and atr_pct[i - 1] <= atr_pct_smooth[i - 1]:
            if (i - last_high_vol_idx) > cooldown // 2:
                label.new(
                    x=i, y=float(atr_pct[i]),
                    text="Expansion",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#42a5f5",
                    size="tiny"
                )
