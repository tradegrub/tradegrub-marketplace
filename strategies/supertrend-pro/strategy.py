from tg_scripting import *
import numpy as np

indicator("Supertrend Pro", overlay=True)

atr_period = input.int(10, "ATR Period", minval=1, maxval=100)
multiplier = input.float(3.0, "Multiplier", minval=0.5, maxval=10.0)
use_trailing = input.bool(True, "Trailing Stop")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr_val = ta.atr(high, low, close, atr_period)
supertrend, direction = ta.supertrend(high, low, close, atr_period, multiplier)

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if ta.crossover(direction, 0)[i]:
        strategy.entry("Long", strategy.LONG)
    if ta.crossunder(direction, 0)[i]:
        strategy.entry("Short", strategy.SHORT)

    if use_trailing:
        trail_offset = atr_val[i] * multiplier
        if direction[i] > 0:
            strategy.exit("Trail Long", "Long", trail_offset=trail_offset)
        else:
            strategy.exit("Trail Short", "Short", trail_offset=trail_offset)

bull = direction[-1] > 0
plot(supertrend, title="SuperTrend", color="green" if bull else "red", linewidth=2)
plotshape(ta.crossover(direction, 0), title="Buy", shape="triangleup", location="belowbar", color="green", size="small")
plotshape(ta.crossunder(direction, 0), title="Sell", shape="triangledown", location="abovebar", color="red", size="small")

# --- Rich annotations ---
n = len(close)
cross_up = ta.crossover(direction, 0)
cross_down = ta.crossunder(direction, 0)
last_signal_idx = -100

for i in range(atr_period, n):
    if cross_up[i] and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(supertrend[i])
            tp_price = entry_price + (entry_price - sl_price) * 2
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down[i] and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(supertrend[i])
            tp_price = entry_price - (sl_price - entry_price) * 2
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(tp_price, sl_price), right=end_bar, bottom=min(tp_price, sl_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
