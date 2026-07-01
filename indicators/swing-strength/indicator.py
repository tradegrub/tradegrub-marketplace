from tg_scripting import *
import numpy as np

indicator("Swing Strength", overlay=False)

swing_len = input.int(5, "Swing Length", minval=2, maxval=20)
vol_weight = input.float(0.4, "Volume Weight", minval=0.0, maxval=1.0)
price_weight = input.float(0.4, "Price Weight", minval=0.0, maxval=1.0)
time_weight = input.float(0.2, "Time Weight", minval=0.0, maxval=1.0)
atr_period = input.int(14, "ATR Period", minval=5, maxval=50)
smooth_len = input.int(3, "Smoothing Length", minval=1, maxval=10)
show_swings = input.bool(True, "Show Swing Markers")
threshold = input.float(0.6, "Significance Threshold", minval=0.1, maxval=2.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

atr = ta.atr(high, low, close, atr_period)
avg_vol = ta.sma(volume, atr_period)

swing_high_val = ta.highest(high, swing_len)
swing_low_val = ta.lowest(low, swing_len)

is_swing_high = (high == swing_high_val) & (high > ta.highest(high, swing_len * 2) * 0.995)
is_swing_low = (low == swing_low_val) & (low < ta.lowest(low, swing_len * 2) * 1.005)

price_disp = np.abs(ta.change(close, swing_len)) / atr
vol_intensity = volume / avg_vol
time_factor = np.ones(len(close))

raw_score = (price_disp * price_weight) + (vol_intensity * vol_weight) + (time_factor * time_weight)
strength = ta.ema(raw_score, smooth_len)

bull_strength = np.where(is_swing_low, strength, np.nan)
bear_strength = np.where(is_swing_high, strength, np.nan)

plot(strength, title="Swing Strength", color="white")
hline(threshold, title="Threshold", color="gray", linestyle="dashed")

if show_swings:
    plotshape(bull_strength > threshold, title="Strong Swing Low", shape="triangle_up",
             location="belowbar", color="lime", size="small")
    plotshape(bear_strength > threshold, title="Strong Swing High", shape="triangle_down",
             location="abovebar", color="red", size="small")

bgcolor(strength > threshold * 1.5, color="rgba(255,255,0,0.1)")

# --- Rich annotations ---
n = len(close)
last_bull_swing_idx = -100
last_bear_swing_idx = -100
cooldown_bars = swing_len * 4

for i in range(swing_len * 2, n):
    if show_labels and is_swing_low[i] and strength[i] > threshold and (i - last_bull_swing_idx) > cooldown_bars:
        last_bull_swing_idx = i
        score_text = "Strong Support" if strength[i] > threshold * 1.5 else "Support"
        label.new(
            x=i, y=float(strength[i]),
            text=score_text,
            style=label.style_label_up,
            color="rgba(0,230,118,0.25)",
            textcolor="#00e676",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(strength[i]), x2=min(i + swing_len * 4, n - 1), y2=float(strength[i]),
                     color="#00e676", width=1, style=line.style_dashed)

    if show_labels and is_swing_high[i] and strength[i] > threshold and (i - last_bear_swing_idx) > cooldown_bars:
        last_bear_swing_idx = i
        score_text = "Strong Resistance" if strength[i] > threshold * 1.5 else "Resistance"
        label.new(
            x=i, y=float(strength[i]),
            text=score_text,
            style=label.style_label_down,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(strength[i]), x2=min(i + swing_len * 4, n - 1), y2=float(strength[i]),
                     color="#ef5350", width=1, style=line.style_dashed)
