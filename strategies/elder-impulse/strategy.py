# Elder Impulse System
from tg_scripting import *
import numpy as np

indicator("Elder Impulse", overlay=True)

ema_length = input.int(13, "EMA Length", minval=5, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=5, maxval=30)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=50)
macd_signal = input.int(9, "MACD Signal", minval=3, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

ema = ta.ema(close, ema_length)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_signal)

ema_rising = ta.change(ema, 1)
hist_rising = ta.change(hist, 1)

# Green bar: both EMA and MACD histogram rising (bullish impulse)
green_bar = (ema_rising[-1] > 0) and (hist_rising[-1] > 0)
# Red bar: both EMA and MACD histogram falling (bearish impulse)
red_bar = (ema_rising[-1] < 0) and (hist_rising[-1] < 0)

if green_bar:
    strategy.entry("Long", strategy.LONG)

if red_bar:
    strategy.entry("Short", strategy.SHORT)

# Exit long on red impulse, exit short on green impulse
if red_bar:
    strategy.close("Long")
if green_bar:
    strategy.close("Short")

plot(ema, title="EMA", color="blue")
plot(hist, title="MACD Histogram", color="gray")
bgcolor(green_bar, color="rgba(0, 200, 0, 0.15)")
bgcolor(red_bar, color="rgba(200, 0, 0, 0.15)")

# --- Rich annotations ---
n = len(close)
ema_rising_arr = ta.change(ema, 1)
hist_rising_arr = ta.change(hist, 1)
green_arr = (ema_rising_arr > 0) & (hist_rising_arr > 0)
red_arr = (ema_rising_arr < 0) & (hist_rising_arr < 0)
atr_ann = ta.atr(high, low, close, 14)
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if green_arr[i] and not green_arr[i - 1]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Bullish Impulse",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr_ann[i] * 1.5)
            tp_price = float(close[i] + atr_ann[i] * 3.0)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif red_arr[i] and not red_arr[i - 1]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Bearish Impulse",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr_ann[i] * 1.5)
            tp_price = float(close[i] - atr_ann[i] * 3.0)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(sl_price, tp_price), right=end_bar, bottom=min(sl_price, tp_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
