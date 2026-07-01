# ATR Trailing Stop Strategy
from tg_scripting import *
import numpy as np

indicator("ATR Trailing Stop", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(3.0, "ATR Multiplier", minval=1.0, maxval=10.0)
sma_len = input.int(50, "Trend SMA Length", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, sma_len)

# Calculate trailing stop levels
trail_long = close - atr_mult * atr
trail_short = close + atr_mult * atr

# Use highest trailing long stop as the effective stop
trail_long_stop = ta.highest(trail_long, atr_len)

# Entry: price above trend SMA
in_uptrend = close[-1] > trend_sma[-1]
in_downtrend = close[-1] < trend_sma[-1]

# Long entry when trending up and price bounces off trailing stop zone
near_stop = close[-1] < trail_long_stop[-1] * 1.02

if in_uptrend and not near_stop:
    strategy.entry("Long", strategy.LONG)

# Exit when price breaks below trailing stop
if close[-1] < trail_long_stop[-1]:
    strategy.close("Long")

# Short entry in downtrend
if in_downtrend:
    strategy.entry("Short", strategy.SHORT)

trail_short_stop = ta.lowest(trail_short, atr_len)
if close[-1] > trail_short_stop[-1]:
    strategy.close("Short")

plot(trail_long_stop, title="Long Trail Stop", color="green")
plot(trail_short_stop, title="Short Trail Stop", color="red")
plot(trend_sma, title="Trend SMA", color="orange")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30
prev_uptrend = False
prev_downtrend = False

for i in range(sma_len, n):
    cur_up = close[i] > trend_sma[i]
    cur_down = close[i] < trend_sma[i]

    # Trend flip up
    if cur_up and not prev_uptrend and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Trend Up",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(trail_long_stop[i])
            tp_price = float(close[i] + (close[i] - trail_long_stop[i]) * 2)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Trail Stop",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    # Trend flip down
    elif cur_down and not prev_downtrend and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Trend Down",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(trail_short_stop[i])
            tp_price = float(close[i] - (trail_short_stop[i] - close[i]) * 2)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Trail Stop",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

    # Stop hit labels
    if show_labels and cur_up and close[i] < trail_long_stop[i] and (i - last_signal_idx) > cooldown // 2:
        label.new(x=i, y=float(close[i]), text="Stop Hit",
                  style=label.style_label_down, color="rgba(239,83,80,0.3)",
                  textcolor="#ef5350", size="small")

    prev_uptrend = cur_up
    prev_downtrend = cur_down
