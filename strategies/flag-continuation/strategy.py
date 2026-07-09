from tg_scripting import *
import numpy as np

indicator("Flag Continuation", overlay=True)

pole_len = input.int(10, "Pole Lookback", minval=5, maxval=30)
flag_len = input.int(5, "Flag Length", minval=3, maxval=15)
pole_atr_mult = input.float(2.0, "Pole ATR Multiple", minval=1.0, maxval=5.0)
flag_retrace_max = input.float(0.5, "Max Retracement", minval=0.2, maxval=0.8)
use_volume = input.bool(True, "Volume Confirmation")
vol_mult = input.float(1.2, "Volume Multiplier", minval=1.0, maxval=3.0)
atr_stop = input.float(1.5, "ATR Stop Multiple", minval=0.5, maxval=4.0)
atr_target = input.float(3.0, "ATR Target Multiple", minval=1.0, maxval=6.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, 14)
avg_vol = ta.sma(volume, 20)
pole_high = ta.highest(high, pole_len)
pole_low = ta.lowest(low, pole_len)
pole_range = pole_high - pole_low

flag_high = ta.highest(high, flag_len)
flag_low = ta.lowest(low, flag_len)
flag_range = flag_high - flag_low

bull_pole = (close - ta.lowest(low, pole_len)) > (pole_atr_mult * atr)
bear_pole = (ta.highest(high, pole_len) - close) > (pole_atr_mult * atr)

bull_flag = (flag_range < flag_retrace_max * pole_range) & (close > pole_low + (1 - flag_retrace_max) * pole_range)
bear_flag = (flag_range < flag_retrace_max * pole_range) & (close < pole_high - (1 - flag_retrace_max) * pole_range)

vol_ok = ~use_volume | (volume > vol_mult * avg_vol)

bull_break = ta.crossover(close, flag_high)
bear_break = ta.crossunder(close, flag_low)

bgcolor(bull_flag & bull_pole, color="rgba(0,200,100,0.05)")
bgcolor(bear_flag & bear_pole, color="rgba(200,0,50,0.05)")

n = len(close)
last_signal_idx = -100

for i in range(len(close)):
    strategy.set_bar_index(i)
    if bull_pole[i] & bull_flag[i] & bull_break[i] & vol_ok[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long", stop=close[i] - atr_stop * atr[i], limit=close[i] + atr_target * atr[i])

        if i - last_signal_idx >= 15:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(low[i]),
                          text="Bull Flag\nBREAKOUT",
                          style=label.style_label_up,
                          color="#00e676", textcolor="#000000", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] - atr_stop * atr[i])
                tp_price = float(close[i] + atr_target * atr[i])
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

    elif bear_pole[i] & bear_flag[i] & bear_break[i] & vol_ok[i]:
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short", stop=close[i] + atr_stop * atr[i], limit=close[i] - atr_target * atr[i])

        if i - last_signal_idx >= 15:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(high[i]),
                          text="Bear Flag\nBREAKDOWN",
                          style=label.style_label_down,
                          color="#ef5350", textcolor="#ffffff", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] + atr_stop * atr[i])
                tp_price = float(close[i] - atr_target * atr[i])
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

plotshape(bull_pole & bull_flag & bull_break & vol_ok, style="triangleup", location="belowbar", color="green", title="Bull Flag")
plotshape(bear_pole & bear_flag & bear_break & vol_ok, style="triangledown", location="abovebar", color="red", title="Bear Flag")
plot(atr, title="ATR", color="gray", display="none")

flag_active = bull_flag | bear_flag
p_flag_high = plot([(float(flag_high[i]) if flag_active[i] else None) for i in range(n)], title="Flag High", color="#42a5f5", linewidth=1)
p_flag_low = plot([(float(flag_low[i]) if flag_active[i] else None) for i in range(n)], title="Flag Low", color="#42a5f5", linewidth=1)
fill(p_flag_high, p_flag_low, color="rgba(66,165,245,0.08)", title="Flag Channel")
