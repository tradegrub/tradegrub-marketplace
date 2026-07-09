# Linear Regression Deviation Reversion
from tg_scripting import *
import numpy as np

strategy("Regression Reversion", overlay=True)

reg_length = input.int(50, "Regression Length", minval=10, maxval=200)
dev_threshold = input.float(2.0, "Deviation Threshold %", minval=0.5, maxval=10.0)
exit_pct = input.float(0.5, "Exit Deviation %", minval=0.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

linreg = ta.linreg(close, reg_length)

# Calculate percentage deviation from regression
deviation_pct = ((close - linreg) / linreg) * 100

# Enter when price deviates too far from regression
if deviation_pct[-1] < -dev_threshold and deviation_pct[-2] >= -dev_threshold:
    strategy.entry("Long", strategy.LONG)

if deviation_pct[-1] > dev_threshold and deviation_pct[-2] <= dev_threshold:
    strategy.entry("Short", strategy.SHORT)

# Exit when deviation normalizes
if deviation_pct[-1] > -exit_pct and deviation_pct[-2] <= -exit_pct:
    strategy.close("Long")
if deviation_pct[-1] < exit_pct and deviation_pct[-2] >= exit_pct:
    strategy.close("Short")

plot(deviation_pct, title="Deviation %", color="purple")
hline(dev_threshold, title="Upper Threshold", color="red")
hline(-dev_threshold, title="Lower Threshold", color="green")
hline(0, title="Zero", color="gray")

bgcolor(deviation_pct[-1] < -dev_threshold, color="rgba(76, 175, 80, 0.1)")
bgcolor(deviation_pct[-1] > dev_threshold, color="rgba(244, 67, 54, 0.1)")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 30
cooldown = reg_length // 2

for i in range(reg_length, n):
    # Long entry: deviation crosses below -threshold
    if i > 0 and deviation_pct[i] < -dev_threshold and deviation_pct[i - 1] >= -dev_threshold and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Oversold\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            tp_price = float(linreg[i])
            risk = entry_price - tp_price
            sl_price = float(entry_price + risk)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Regression",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(entry_price, tp_price), right=end_bar, bottom=min(entry_price, tp_price),
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    # Short entry: deviation crosses above +threshold
    elif i > 0 and deviation_pct[i] > dev_threshold and deviation_pct[i - 1] <= dev_threshold and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Overbought\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            tp_price = float(linreg[i])
            risk = tp_price - entry_price
            sl_price = float(entry_price - risk)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Regression",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(entry_price, tp_price), right=end_bar, bottom=min(entry_price, tp_price),
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")
