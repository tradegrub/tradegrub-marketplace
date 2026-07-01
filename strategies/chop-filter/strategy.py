# Choppiness Index Filter + EMA Trend
from tg_scripting import *
import numpy as np

indicator("Chop Filter", overlay=True)

chop_length = input.int(14, "Choppiness Length", minval=5, maxval=50)
ema_fast = input.int(12, "Fast EMA", minval=5, maxval=50)
ema_slow = input.int(26, "Slow EMA", minval=10, maxval=100)
chop_threshold = input.float(50.0, "Chop Threshold", minval=30.0, maxval=70.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

chop = ta.chop(high, low, close, chop_length)
fast = ta.ema(close, ema_fast)
slow = ta.ema(close, ema_slow)

is_trending = chop[-1] < chop_threshold

# Only trade when market is trending (low choppiness)
if is_trending and ta.crossover(fast, slow)[-1]:
    strategy.entry("Long", strategy.LONG)

if is_trending and ta.crossunder(fast, slow)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit if market becomes choppy
if chop[-1] > 61.8:
    strategy.close_all()

plot(chop, title="Choppiness Index", color="purple")
hline(chop_threshold, title="Trend Threshold", color="green")
hline(61.8, title="Chop Threshold", color="red")
plot(fast, title="Fast EMA", color="blue")
plot(slow, title="Slow EMA", color="orange")

# --- Rich annotations ---
ema_cross_up = ta.crossover(fast, slow)
ema_cross_down = ta.crossunder(fast, slow)
atr = ta.atr(high, low, close, 14)
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30

for i in range(1, n):
    trending_i = chop[i] < chop_threshold

    if trending_i and ema_cross_up[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG\nGolden Cross",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
            label.new(x=i, y=float(low[i] - atr[i] * 0.5), text="Trending",
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#42a5f5", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2)
            tp_price = float(close[i] + atr[i] * 3)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif trending_i and ema_cross_down[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT\nDeath Cross",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * 2)
            tp_price = float(close[i] - atr[i] * 3)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

    # Label choppy zones
    if show_labels and chop[i] > 61.8 and (i > 1 and chop[i - 1] <= 61.8):
        label.new(x=i, y=float(high[i]), text="Choppy",
                  style=label.style_label_down, color="rgba(156,39,176,0.3)",
                  textcolor="#9c27b0", size="small")
