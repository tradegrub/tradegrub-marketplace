from tg_scripting import *

indicator("EMA Volume Breakout", overlay=True)

# Inputs
ema_fast = input.int(9, "Fast EMA", minval=2, maxval=50)
ema_slow = input.int(21, "Slow EMA", minval=5, maxval=100)
vol_mult = input.float(1.5, "Volume Surge Multiplier", minval=1.0, maxval=5.0)
vol_avg_len = input.int(20, "Volume Average Length", minval=5, maxval=50)
lookback = input.int(20, "Breakout Lookback", minval=5, maxval=100)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
ema_f = ta.ema(close, ema_fast)
ema_s = ta.ema(close, ema_slow)
vol_avg = ta.sma(volume, vol_avg_len)
volume_surge = volume > (vol_avg * vol_mult)

# Breakout levels
high_break = ta.highest(high, lookback)
low_break = ta.lowest(low, lookback)

# EMA uptrend + volume surge + price breakout
uptrend = ema_f > ema_s
downtrend = ema_f < ema_s

long_cond = uptrend & volume_surge & (close >= high_break)
short_cond = downtrend & volume_surge & (close <= low_break)

import numpy as np
atr_ann = ta.atr(high, low, close, 14)
n = len(close)
last_signal_idx = -100

for i in range(len(close)):
    strategy.set_bar_index(i)
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

    if i - last_signal_idx < 15:
        continue

    if long_cond[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="BREAKOUT",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
            label.new(x=i, y=float(low[i] - atr_ann[i] * 0.5),
                      text="Vol Surge",
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#42a5f5", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr_ann[i] * 1.5)
            tp_price = float(close[i] + atr_ann[i] * 3.0)
            end_bar = min(i + 30, n - 1)
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

    elif short_cond[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="BREAKDOWN",
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
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

# Plots
plot(ema_f, title="Fast EMA", color="green")
plot(ema_s, title="Slow EMA", color="red")
plot(high_break, title="Breakout High", color="#42a5f5")
plot(low_break, title="Breakout Low", color="maroon")
bgcolor(volume_surge, color="rgba(0, 150, 255, 0.1)")

plotshape(long_cond, title="Breakout Signal", style="triangleup", location="belowbar", color="#00e676")
plotshape(short_cond, title="Breakdown Signal", style="triangledown", location="abovebar", color="#ef5350")

# Highlight breakout/breakdown bars to match the glow zone in the concept art
bgcolor([("rgba(0,230,118,0.12)" if long_cond[i] else ("rgba(239,83,80,0.12)" if short_cond[i] else None)) for i in range(n)])
