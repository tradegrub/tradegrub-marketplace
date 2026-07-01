from tg_scripting import *
import numpy as np

indicator("Liquidity Sweep", overlay=True)

lookback = input.int(10, "Swing Lookback", minval=5, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
sweep_mult = input.float(0.1, "Sweep Threshold (ATR)", minval=0.01, maxval=1.0)
min_wick_ratio = input.float(0.5, "Min Wick Ratio", minval=0.1, maxval=1.0)
show_zones = input.bool(True, "Show Liquidity Zones")
show_labels = input.bool(True, "Show Sweep Labels")
show_levels = input.bool(True, "Show Levels")
bull_color = input.color("#00e676", "Bullish Sweep")
bear_color = input.color("#ff1744", "Bearish Sweep")

atr = ta.atr(high, low, close, atr_len)
swing_high = ta.highest(high, lookback)
swing_low = ta.lowest(low, lookback)

prev_swing_high = np.roll(swing_high, 1)
prev_swing_low = np.roll(swing_low, 1)
prev_swing_high[0] = np.nan
prev_swing_low[0] = np.nan

threshold = atr * sweep_mult

high_sweep = (high > prev_swing_high + threshold) & (close < prev_swing_high)
low_sweep = (low < prev_swing_low - threshold) & (close > prev_swing_low)

body = np.abs(close - open)
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low
total_range = high - low + 1e-10

bear_wick_valid = upper_wick / total_range >= min_wick_ratio
bull_wick_valid = lower_wick / total_range >= min_wick_ratio

bearish_sweep = high_sweep & bear_wick_valid
bullish_sweep = low_sweep & bull_wick_valid

if show_zones:
    plot(prev_swing_high, title="Resistance Zone", color=bear_color, linewidth=1, style="stepline")
    plot(prev_swing_low, title="Support Zone", color=bull_color, linewidth=1, style="stepline")

if show_labels:
    plotshape(bullish_sweep, title="Bull Sweep", shape="triangleup", location="belowbar", color=bull_color, size="small")
    plotshape(bearish_sweep, title="Bear Sweep", shape="triangledown", location="abovebar", color=bear_color, size="small")


sweep_score = np.where(bullish_sweep, 1, np.where(bearish_sweep, -1, 0))
plot(sweep_score, title="Sweep Signal", display="none")

# --- Rich annotations ---
n = len(close)
last_bull_sweep_idx = -100
last_bear_sweep_idx = -100
cooldown = 15

for i in range(lookback, n):
    if show_labels:
        # Bullish liquidity sweep with label
        if bullish_sweep[i] and (i - last_bull_sweep_idx) > cooldown:
            label.new(
                x=i, y=float(low[i]),
                text="Bull Sweep",
                style=label.style_label_up,
                color="rgba(0,230,118,0.3)",
                textcolor="#00e676",
                size="normal"
            )
            last_bull_sweep_idx = i

        # Bearish liquidity sweep with label
        if bearish_sweep[i] and (i - last_bear_sweep_idx) > cooldown:
            label.new(
                x=i, y=float(high[i]),
                text="Bear Sweep",
                style=label.style_label_down,
                color="rgba(255,23,68,0.3)",
                textcolor="#ff1744",
                size="normal"
            )
            last_bear_sweep_idx = i

    if show_levels:
        # Draw the swept liquidity level line
        if bullish_sweep[i] and (i - last_bull_sweep_idx) == 0:
            line.new(
                x1=max(0, i - lookback), y1=float(prev_swing_low[i]),
                x2=i, y2=float(prev_swing_low[i]),
                color="#00e676", width=1, style=line.style_dotted
            )
        if bearish_sweep[i] and (i - last_bear_sweep_idx) == 0:
            line.new(
                x1=max(0, i - lookback), y1=float(prev_swing_high[i]),
                x2=i, y2=float(prev_swing_high[i]),
                color="#ff1744", width=1, style=line.style_dotted
            )
