# ADX Trend Strategy
from tg_scripting import *
import numpy as np

indicator("ADX Trend", overlay=True)

di_len = input.int(14, "DI Length", minval=5, maxval=50)
adx_len = input.int(14, "ADX Smoothing", minval=5, maxval=50)
adx_thresh = input.float(25.0, "ADX Threshold", minval=15.0, maxval=50.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

plus_di, minus_di, adx_val = ta.dmi(high, low, close, di_len)


di_cross_up = ta.crossover(plus_di, minus_di)
di_cross_down = ta.crossunder(plus_di, minus_di)

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if di_cross_up[i] and (adx_val[i] > adx_thresh):
        strategy.entry("Long", strategy.LONG)
    if di_cross_down[i]:
        strategy.close("Long")

plot(plus_di, title="+DI", color="green")
plot(minus_di, title="-DI", color="red")
plot(adx_val, title="ADX", color="blue")
hline(adx_thresh, title="Threshold", color="gray")

# --- Rich annotations ---
atr = ta.atr(high, low, close, 14)
di_cross_up_arr = ta.crossover(plus_di, minus_di)
di_cross_down_arr = ta.crossunder(plus_di, minus_di)
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30

for i in range(1, n):
    strong = adx_val[i] > adx_thresh
    if di_cross_up_arr[i] and strong and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG\n+DI Cross",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
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

    elif di_cross_down_arr[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="EXIT\n-DI Cross",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
