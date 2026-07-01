from tg_scripting import *
import numpy as np

indicator("Higher Low Tracker", overlay=True)

swing_len = input.int(5, "Swing Length", minval=2, maxval=50)
min_touches = input.int(3, "Min Touches", minval=2, maxval=10)
break_atr_mult = input.float(1.5, "Break ATR Mult", minval=0.5, maxval=5.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
show_hl_line = input.bool(True, "Show HL Trendline")
show_lh_line = input.bool(True, "Show LH Trendline")
smooth_len = input.int(3, "Smooth Length", minval=1, maxval=10)
alert_break = input.bool(True, "Alert on Break")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

atr = ta.atr(high, low, close, atr_len)
smoothed_low = ta.sma(low, smooth_len)
smoothed_high = ta.sma(high, smooth_len)

swing_low = ta.lowest(smoothed_low, swing_len)
swing_high = ta.highest(smoothed_high, swing_len)

is_swing_low = (smoothed_low == swing_low)
is_swing_high = (smoothed_high == swing_high)

hl_trendline = np.full(len(close), np.nan)
lh_trendline = np.full(len(close), np.nan)
hl_break = np.zeros(len(close), dtype=bool)
lh_break = np.zeros(len(close), dtype=bool)

prev_swing_low = np.nan
prev_swing_low_idx = 0
prev_swing_high = np.nan
prev_swing_high_idx = 0
hl_count = 0
lh_count = 0

for i in range(swing_len, len(close)):
    if is_swing_low[i]:
        if not np.isnan(prev_swing_low) and smoothed_low[i] > prev_swing_low:
            hl_count += 1
            if hl_count >= min_touches - 1 and prev_swing_low_idx > 0:
                slope = (smoothed_low[i] - prev_swing_low) / (i - prev_swing_low_idx)
                for j in range(prev_swing_low_idx, min(i + 1, len(close))):
                    hl_trendline[j] = prev_swing_low + slope * (j - prev_swing_low_idx)
        else:
            hl_count = 0
        prev_swing_low = smoothed_low[i]
        prev_swing_low_idx = i

    if is_swing_high[i]:
        if not np.isnan(prev_swing_high) and smoothed_high[i] < prev_swing_high:
            lh_count += 1
            if lh_count >= min_touches - 1 and prev_swing_high_idx > 0:
                slope = (smoothed_high[i] - prev_swing_high) / (i - prev_swing_high_idx)
                for j in range(prev_swing_high_idx, min(i + 1, len(close))):
                    lh_trendline[j] = prev_swing_high + slope * (j - prev_swing_high_idx)
        else:
            lh_count = 0
        prev_swing_high = smoothed_high[i]
        prev_swing_high_idx = i

    if not np.isnan(hl_trendline[i]) and close[i] < hl_trendline[i] - break_atr_mult * atr[i]:
        hl_break[i] = True
    if not np.isnan(lh_trendline[i]) and close[i] > lh_trendline[i] + break_atr_mult * atr[i]:
        lh_break[i] = True

if show_hl_line:
    plot(hl_trendline, title="HL Trendline", color="green", linewidth=2)
if show_lh_line:
    plot(lh_trendline, title="LH Trendline", color="red", linewidth=2)

plotshape(hl_break, title="HL Break", shape="triangledown", location="abovebar", color="red", size="small")
plotshape(lh_break, title="LH Break", shape="triangleup", location="belowbar", color="green", size="small")
bgcolor(hl_break, color="rgba(255,0,0,0.1)")
bgcolor(lh_break, color="rgba(0,255,0,0.1)")

# --- Rich annotations ---
last_hl_label_idx = -100
last_lh_label_idx = -100
last_hl_break_label = -100
last_lh_break_label = -100
cooldown = 15

for i in range(swing_len, len(close)):
    if show_labels:
        # Label higher low swing points
        if is_swing_low[i] and not np.isnan(hl_trendline[i]) and (i - last_hl_label_idx) > cooldown:
            label.new(
                x=i, y=float(smoothed_low[i]),
                text="HL",
                style=label.style_label_up,
                color="rgba(0,230,118,0.2)",
                textcolor="#00e676",
                size="small"
            )
            last_hl_label_idx = i

        # Label lower high swing points
        if is_swing_high[i] and not np.isnan(lh_trendline[i]) and (i - last_lh_label_idx) > cooldown:
            label.new(
                x=i, y=float(smoothed_high[i]),
                text="LH",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_lh_label_idx = i

    if show_levels:
        # HL trendline break
        if hl_break[i] and (i - last_hl_break_label) > cooldown:
            label.new(
                x=i, y=float(high[i]),
                text="HL Break",
                style=label.style_label_down,
                color="rgba(239,83,80,0.3)",
                textcolor="#ef5350",
                size="normal"
            )
            last_hl_break_label = i

        # LH trendline break (bullish breakout)
        if lh_break[i] and (i - last_lh_break_label) > cooldown:
            label.new(
                x=i, y=float(low[i]),
                text="LH Break",
                style=label.style_label_up,
                color="rgba(0,230,118,0.3)",
                textcolor="#00e676",
                size="normal"
            )
            last_lh_break_label = i
