from tg_scripting import *
import numpy as np
from sklearn.linear_model import LinearRegression

indicator("Statistical Mean Reversion", overlay=True)

smooth_len = input.int(50, "Smoothing Period", minval=10, maxval=200)
zscore_len = input.int(20, "Z-Score Lookback", minval=5, maxval=100)
entry_z = input.float(2.0, "Entry Z-Score", minval=0.5, maxval=4.0)
exit_z = input.float(0.0, "Exit Z-Score", minval=-1.0, maxval=1.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_stop = input.float(3.0, "ATR Stop Multiple", minval=1.0, maxval=6.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop Levels")

n = len(close)
atr = ta.atr(high, low, close, atr_len)
smoothed = ta.ema(close, smooth_len)

# Compute hedge ratio using sklearn LinearRegression
close_arr = np.array(close, dtype=float).reshape(-1, 1)
smooth_arr = np.array(smoothed, dtype=float).reshape(-1, 1)

valid_mask = ~(np.isnan(close_arr.ravel()) | np.isnan(smooth_arr.ravel()))
hedge_ratio = 1.0
if np.sum(valid_mask) > 10:
    reg = LinearRegression()
    reg.fit(smooth_arr[valid_mask], close_arr[valid_mask])
    hedge_ratio = float(reg.coef_[0][0])

# Compute spread and z-score
spread = np.array(close, dtype=float) - hedge_ratio * np.array(smoothed, dtype=float)
zscore = np.full(n, np.nan)

for i in range(zscore_len - 1, n):
    window = spread[i - zscore_len + 1:i + 1]
    mu = np.mean(window)
    sigma = np.std(window)
    if sigma > 1e-10:
        zscore[i] = (spread[i] - mu) / sigma

# Generate signals
long_signal = np.zeros(n, dtype=bool)
short_signal = np.zeros(n, dtype=bool)
exit_long_signal = np.zeros(n, dtype=bool)
exit_short_signal = np.zeros(n, dtype=bool)

for i in range(1, n):
    if not np.isnan(zscore[i]) and not np.isnan(zscore[i - 1]):
        if zscore[i] < -entry_z:
            long_signal[i] = True
        if zscore[i] > entry_z:
            short_signal[i] = True
        if zscore[i - 1] < exit_z <= zscore[i]:
            exit_long_signal[i] = True
        if zscore[i - 1] > exit_z >= zscore[i]:
            exit_short_signal[i] = True

# Execute strategy
in_long = False
in_short = False
entry_price_tracked = 0.0

for i in range(n):
    if long_signal[i] and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price_tracked = float(close[i])
    elif short_signal[i] and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price_tracked = float(close[i])

    if in_long:
        sl = entry_price_tracked - float(atr[i]) * atr_stop
        strategy.exit("Long", stop=sl)
        if exit_long_signal[i] or float(close[i]) <= sl:
            if exit_long_signal[i]:
                strategy.close("Long")
            in_long = False

    if in_short:
        sl = entry_price_tracked + float(atr[i]) * atr_stop
        strategy.exit("Short", stop=sl)
        if exit_short_signal[i] or float(close[i]) >= sl:
            if exit_short_signal[i]:
                strategy.close("Short")
            in_short = False

# Plot spread and z-score
plot(spread, title="Spread", color="#42a5f5", linewidth=1)
plot(zscore, title="Z-Score", color="#ff9800", linewidth=2)
hline(float(entry_z), title="Upper Threshold", color="#ef5350", linestyle="dashed")
hline(float(-entry_z), title="Lower Threshold", color="#00e676", linestyle="dashed")
hline(float(exit_z), title="Exit Level", color="#888888", linestyle="dotted")

# Plot smoothed overlay
plot(smoothed, title="Smoothed (EMA)", color="#ff9800", linewidth=2)

# Entry markers
plotshape(long_signal, title="Long Entry", style="triangleup", location="belowbar", color="#00e676")
plotshape(short_signal, title="Short Entry", style="triangledown", location="abovebar", color="#ff1744")

# Background shading for overbought/oversold zones
ob_zone = np.array([not np.isnan(zscore[i]) and zscore[i] > entry_z for i in range(n)])
os_zone = np.array([not np.isnan(zscore[i]) and zscore[i] < -entry_z for i in range(n)])
bgcolor(ob_zone, color="rgba(239,83,80,0.08)")
bgcolor(os_zone, color="rgba(0,230,118,0.08)")

# Labels and level annotations
last_long_ann = -100
last_short_ann = -100
last_exit_ann = -100
cooldown = 20
ann_bars = 25

for i in range(n):
    if long_signal[i] and (i - last_long_ann) > cooldown:
        last_long_ann = i
        if show_labels:
            z_val = f"{zscore[i]:.1f}" if not np.isnan(zscore[i]) else "?"
            label.new(x=i, y=float(low[i]), text=f"LONG\nz={z_val}",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            ep = float(close[i])
            sl = ep - float(atr[i]) * atr_stop
            end = min(i + ann_bars, n - 1)
            line.new(x1=i, y1=ep, x2=end, y2=ep,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ep, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl, x2=end, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            box.new(left=i, top=ep, right=end, bottom=sl,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    if short_signal[i] and (i - last_short_ann) > cooldown:
        last_short_ann = i
        if show_labels:
            z_val = f"{zscore[i]:.1f}" if not np.isnan(zscore[i]) else "?"
            label.new(x=i, y=float(high[i]), text=f"SHORT\nz={z_val}",
                      style=label.style_label_down, color="#ff1744",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            ep = float(close[i])
            sl = ep + float(atr[i]) * atr_stop
            end = min(i + ann_bars, n - 1)
            line.new(x1=i, y1=ep, x2=end, y2=ep,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ep, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl, x2=end, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            box.new(left=i, top=sl, right=end, bottom=ep,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

    if (exit_long_signal[i] or exit_short_signal[i]) and (i - last_exit_ann) > cooldown:
        last_exit_ann = i
        if show_labels:
            label.new(x=i, y=float(close[i]), text="EXIT\nmean",
                      style=label.style_label_right, color="rgba(136,136,136,0.3)",
                      textcolor="#888888", size="small")
