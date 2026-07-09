from tg_scripting import *
import numpy as np
from scipy.signal import argrelextrema

indicator("Savitzky-Golay Peak Reversal", overlay=True)

order = input.int(5, "Peak Order", minval=2, maxval=20)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_stop = input.float(2.0, "ATR Stop Multiple", minval=1.0, maxval=5.0)
tp_ratio = input.float(2.5, "Take Profit Ratio", minval=1.0, maxval=5.0)
min_swing_pct = input.float(0.5, "Min Swing %", minval=0.1, maxval=5.0)
confirm_bars = input.int(2, "Confirmation Bars", minval=1, maxval=5)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
n = len(close)

peak_idx = argrelextrema(high, np.greater_equal, order=order)[0]
trough_idx = argrelextrema(low, np.less_equal, order=order)[0]

long_signal = np.zeros(n, dtype=bool)
short_signal = np.zeros(n, dtype=bool)

last_trough_price = np.nan
last_trough_bar = -100
last_peak_price = np.nan
last_peak_bar = -100

for i in range(n):
    for t in trough_idx:
        if t == i - confirm_bars and t >= 0:
            last_trough_price = float(low[t])
            last_trough_bar = t

    for p in peak_idx:
        if p == i - confirm_bars and p >= 0:
            last_peak_price = float(high[p])
            last_peak_bar = p

    if not np.isnan(last_trough_price) and i > last_trough_bar + confirm_bars - 1:
        pct_above = (float(close[i]) - last_trough_price) / last_trough_price * 100
        if pct_above >= min_swing_pct and float(close[i]) > float(close[i - 1]):
            long_signal[i] = True
            last_trough_price = np.nan

    if not np.isnan(last_peak_price) and i > last_peak_bar + confirm_bars - 1:
        pct_below = (last_peak_price - float(close[i])) / last_peak_price * 100
        if pct_below >= min_swing_pct and float(close[i]) < float(close[i - 1]):
            short_signal[i] = True
            last_peak_price = np.nan

in_long = False
in_short = False
entry_price_tracked = 0.0

for i in range(n):
    strategy.set_bar_index(i)
    if long_signal[i] and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price_tracked = float(close[i])
    elif short_signal[i] and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price_tracked = float(close[i])

    if in_long:
        sl = entry_price_tracked - float(atr[i]) * atr_stop
        tp = entry_price_tracked + float(atr[i]) * atr_stop * tp_ratio
        strategy.exit("Long", stop=sl, limit=tp)
        if float(close[i]) <= sl or float(close[i]) >= tp:
            in_long = False

    if in_short:
        sl = entry_price_tracked + float(atr[i]) * atr_stop
        tp = entry_price_tracked - float(atr[i]) * atr_stop * tp_ratio
        strategy.exit("Short", stop=sl, limit=tp)
        if float(close[i]) >= sl or float(close[i]) <= tp:
            in_short = False

plotshape(long_signal, title="Long Entry", style="triangleup", location="belowbar", color="#00e676")
plotshape(short_signal, title="Short Entry", style="triangledown", location="abovebar", color="#ff1744")

last_long_ann = -100
last_short_ann = -100
cooldown = 20
ann_bars = 25

for i in range(n):
    if long_signal[i] and (i - last_long_ann) > cooldown:
        last_long_ann = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="REVERSAL\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            ep = float(close[i])
            sl = ep - float(atr[i]) * atr_stop
            tp = ep + float(atr[i]) * atr_stop * tp_ratio
            end = min(i + ann_bars, n - 1)
            line.new(x1=i, y1=ep, x2=end, y2=ep,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ep, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl, x2=end, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp, x2=end, y2=tp,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp, right=end, bottom=sl,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    if short_signal[i] and (i - last_short_ann) > cooldown:
        last_short_ann = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="REVERSAL\nSHORT",
                      style=label.style_label_down, color="#ff1744",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            ep = float(close[i])
            sl = ep + float(atr[i]) * atr_stop
            tp = ep - float(atr[i]) * atr_stop * tp_ratio
            end = min(i + ann_bars, n - 1)
            line.new(x1=i, y1=ep, x2=end, y2=ep,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ep, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl, x2=end, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp, x2=end, y2=tp,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl, right=end, bottom=tp,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

last_peak_ann = -100
last_trough_ann = -100

for i in peak_idx:
    if show_labels and (i - last_peak_ann) > cooldown:
        last_peak_ann = i
        label.new(x=i, y=float(high[i]), text="Peak",
                  style=label.style_label_down, color="rgba(239,83,80,0.2)",
                  textcolor="#ef5350", size="tiny")

for i in trough_idx:
    if show_labels and (i - last_trough_ann) > cooldown:
        last_trough_ann = i
        label.new(x=i, y=float(low[i]), text="Trough",
                  style=label.style_label_up, color="rgba(102,187,106,0.2)",
                  textcolor="#66bb6a", size="tiny")
