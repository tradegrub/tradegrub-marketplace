# NR7 (Narrowest Range of 7) Breakout Strategy
from tg_scripting import *
import numpy as np

indicator("Narrow Range", overlay=True)

nr_period = input.int(7, "NR Period", minval=4, maxval=14)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_tp_mult = input.float(2.5, "ATR Take Profit Multiplier", minval=1.0, maxval=5.0)
atr_sl_mult = input.float(1.0, "ATR Stop Loss Multiplier", minval=0.5, maxval=3.0)
use_volume = input.bool(True, "Require Volume Surge on Breakout")
vol_mult = input.float(1.3, "Volume Surge Multiplier", minval=1.0, maxval=3.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Current bar range
bar_range = high - low
atr = ta.atr(high, low, close, atr_length)

# NR detection: current bar has the narrowest range of the last N bars
min_range = ta.lowest(bar_range, nr_period)
is_nr = bar_range <= min_range

# Volume filter
avg_vol = ta.sma(volume, 20)
vol_surge = volume > avg_vol * vol_mult if use_volume else np.ones(len(close), dtype=bool)

# Trade the breakout of the NR bar on the following bar
nr_prev = np.roll(is_nr, 1)
prev_high = np.roll(high, 1)
prev_low = np.roll(low, 1)

long_signal = nr_prev & (close > prev_high) & vol_surge
short_signal = nr_prev & (close < prev_low) & vol_surge

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if long_signal[i]:
        strategy.entry("Long", strategy.LONG)

    if short_signal[i]:
        strategy.entry("Short", strategy.SHORT)

    # ATR-based exits
    strategy.exit("Long TP/SL", from_entry="Long",
                  limit=close[i] + atr[i] * atr_tp_mult,
                  stop=close[i] - atr[i] * atr_sl_mult)
    strategy.exit("Short TP/SL", from_entry="Short",
              limit=close[i] - atr[i] * atr_tp_mult,
              stop=close[i] + atr[i] * atr_sl_mult)

plot(atr, title="ATR", color="purple")
bgcolor(is_nr, color="rgba(255, 193, 7, 0.15)")
plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 15
nr_label_placed = False

for i in range(nr_period + 1, n):
    # Label the NR zone once
    if show_labels and not nr_label_placed and is_nr[i]:
        nr_label_placed = True
        label.new(
            x=i, y=float(high[i]),
            text="NR" + str(nr_period),
            style=label.style_label_down,
            color="rgba(255,193,7,0.3)",
            textcolor="#FFC107",
            size="small"
        )

    if long_signal[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="LONG\nNR Breakout",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_sl_mult)
            tp_price = float(close[i] + atr[i] * atr_tp_mult)
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

    elif short_signal[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="SHORT\nNR Breakout",
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_sl_mult)
            tp_price = float(close[i] - atr[i] * atr_tp_mult)
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
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
