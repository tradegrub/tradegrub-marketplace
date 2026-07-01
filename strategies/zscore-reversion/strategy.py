# Z-Score Mean Reversion
from tg_scripting import *
import numpy as np

indicator("Zscore Reversion", overlay=True)

length = input.int(20, "Lookback Length", minval=5, maxval=200)
entry_z = input.float(2.0, "Entry Z-Score", minval=1.0, maxval=4.0)
exit_z = input.float(0.0, "Exit Z-Score", minval=-1.0, maxval=1.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

sma = ta.sma(close, length)
stdev = ta.stdev(close, length)
zscore = (close - sma) / stdev

# Buy when Z-score drops below negative threshold (oversold)
if ta.crossover(zscore, -entry_z)[-1]:
    strategy.entry("Long", strategy.LONG)

# Sell when Z-score rises above positive threshold (overbought)
if ta.crossunder(zscore, entry_z)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when Z-score returns to exit level
if zscore[-1] > exit_z and zscore[-2] <= exit_z:
    strategy.close("Long")
if zscore[-1] < -exit_z and zscore[-2] >= -exit_z:
    strategy.close("Short")

plot(zscore, title="Z-Score", color="blue")
hline(entry_z, title="Upper Threshold", color="red")
hline(-entry_z, title="Lower Threshold", color="green")
hline(0, title="Zero Line", color="gray")

# --- Rich annotations ---
n = len(close)
atr = ta.atr(high, low, close, 14)
cross_up_neg = ta.crossover(zscore, -entry_z)
cross_down_pos = ta.crossunder(zscore, entry_z)
last_signal_idx = -100

for i in range(length, n):
    if cross_up_neg[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Oversold\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2)
            tp_price = float(sma[i])
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="TP (Mean)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(tp_price, entry_price), right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down_pos[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Overbought\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * 2)
            tp_price = float(sma[i])
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="TP (Mean)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=min(tp_price, entry_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
