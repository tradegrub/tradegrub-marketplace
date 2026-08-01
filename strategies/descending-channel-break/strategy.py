from tg_scripting import *
import numpy as np

indicator("Descending Channel Break", overlay=True)

length = input.int(20, "Channel Length", minval=10, maxval=100)
vol_mult = input.float(1.5, "Volume Multiplier", minval=1.0, maxval=5.0)
atr_mult = input.float(2.0, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
use_volume_filter = input.bool(True, "Volume Filter")
exit_bars = input.int(30, "Max Hold Bars", minval=5, maxval=100)
rsi_filter = input.bool(True, "RSI Oversold Filter")
rsi_len = input.int(14, "RSI Length", minval=5, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

upper = ta.linreg(high, length, 0)
lower = ta.linreg(low, length, 0)
upper_slope = ta.change(upper, 1)
lower_slope = ta.change(lower, 1)

descending = (upper_slope < 0) & (lower_slope < 0)

avg_vol = ta.sma(volume, length)
vol_surge = volume > (avg_vol * vol_mult)

atr = ta.atr(high, low, close, atr_len)
rsi = ta.rsi(close, rsi_len)

breakout = (close > upper) & descending

if use_volume_filter:
    breakout = breakout & vol_surge

if rsi_filter:
    rsi_prev_oversold = ta.lowest(rsi, length) < 35
    breakout = breakout & rsi_prev_oversold

stop_loss = close - (atr * atr_mult)
take_profit = close + (atr * atr_mult * 2)

plot(upper, title="Upper Channel", color="#ef5350", linewidth=2)
plot(lower, title="Lower Channel", color="#26a69a", linewidth=2)
fill(upper, lower, title="Channel Fill", color="rgba(239,83,80,0.08)")

bgcolor(descending, color="rgba(255,0,0,0.04)")

plotshape(breakout, title="Breakout", shape="triangleup", location="belowbar", color="#00e676", size="small")

n = len(close)
breakout_zone = [(breakout[max(0, i - 3):i + 1].any() if hasattr(breakout, "any") else any(breakout[max(0, i - 3):i + 1])) for i in range(n)]
bgcolor([("rgba(0,230,118,0.10)" if breakout_zone[i] else None) for i in range(n)])

# --- Rich annotations: labels, lines, boxes on chart ---

channel_label_placed = False
last_breakout_idx = -100

bars_held = 0
for i in range(length, n):
    strategy.set_bar_index(i)
    # Label the descending channel zone once near the middle
    if show_labels and not channel_label_placed and descending[i]:
        channel_start = max(0, i - length)
        channel_bars = 0
        for j in range(channel_start, min(n, i + length)):
            if descending[j]:
                channel_bars += 1
        if channel_bars >= length // 2:
            mid = i
            label.new(
                x=mid, y=float(upper[mid]),
                text="Descending Channel",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="normal"
            )
            channel_label_placed = True

    if breakout[i] and (i - last_breakout_idx) > length:
        last_breakout_idx = i

        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="BREAKOUT",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )

            if vol_surge[i]:
                label.new(
                    x=i, y=float(low[i] - atr[i] * 0.5),
                    text="Vol Surge",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#42a5f5",
                    size="small"
                )

        if show_levels:
            entry_price = float(close[i])
            sl_price = float(stop_loss[i])
            tp_price = float(take_profit[i])
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
            label.new(x=i + 2, y=tp_price, text="Take Profit (2:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")

            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long", stop=stop_loss[i], limit=take_profit[i])
        bars_held = 0

    if strategy.position_size > 0:
        bars_held += 1
        if bars_held >= exit_bars:
            strategy.close("Long")
            bars_held = 0
    else:
        bars_held = 0
