# EMA Distance Mean Reversion
from tg_scripting import *
import numpy as np

strategy("EMA Distance", overlay=True)

ema_length = input.int(21, "EMA Length", minval=5, maxval=200)
distance_pct = input.float(3.0, "Distance Threshold %", minval=1.0, maxval=15.0)
exit_pct = input.float(0.5, "Exit Distance %", minval=0.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

ema = ta.ema(close, ema_length)

# Percentage distance from EMA
dist = ((close - ema) / ema) * 100

# Enter long when price is too far below EMA
if dist[-1] < -distance_pct and dist[-2] >= -distance_pct:
    strategy.entry("Long", strategy.LONG)

# Enter short when price is too far above EMA
if dist[-1] > distance_pct and dist[-2] <= distance_pct:
    strategy.entry("Short", strategy.SHORT)

# Exit when price returns near EMA
if dist[-1] > -exit_pct and dist[-2] <= -exit_pct:
    strategy.close("Long")
if dist[-1] < exit_pct and dist[-2] >= exit_pct:
    strategy.close("Short")

plot(ema, title="EMA", color="orange")
plot(dist, title="EMA Distance %", color="blue")
hline(distance_pct, title="Upper Distance", color="red")
hline(-distance_pct, title="Lower Distance", color="green")
hline(0, title="Zero", color="gray")

# --- Rich annotations ---
n = len(close)
atr_ann = ta.atr(high, low, close, 14)
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if dist[i] < -distance_pct and dist[i - 1] >= -distance_pct:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Oversold\nLONG",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr_ann[i] * 1.5)
            tp_price = float(ema[i])
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="EMA Target",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(tp_price, entry_price), right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif dist[i] > distance_pct and dist[i - 1] <= distance_pct:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Overbought\nSHORT",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr_ann[i] * 1.5)
            tp_price = float(ema[i])
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="EMA Target",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=min(tp_price, entry_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
