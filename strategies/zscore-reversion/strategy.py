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
n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if ta.crossover(zscore, -entry_z)[i]:
        strategy.entry("Long", strategy.LONG)

    # Sell when Z-score rises above positive threshold (overbought)
    if ta.crossunder(zscore, entry_z)[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit when Z-score returns to exit level
    if zscore[i] > exit_z and zscore[i-1] <= exit_z:
        strategy.close("Long")
    if zscore[i] < -exit_z and zscore[i-1] >= -exit_z:
        strategy.close("Short")

plot(sma, title="SMA", color="#ff9800", linewidth=1)
plot(zscore, title="Z-Score", color="#42a5f5", linewidth=2)
hline(entry_z, title="Upper Threshold", color="#ef5350", linestyle="dashed")
hline(-entry_z, title="Lower Threshold", color="#00e676", linestyle="dashed")
hline(0, title="Zero Line", color="gray", linestyle="dotted")

cross_up_neg = ta.crossover(zscore, -entry_z)
cross_down_pos = ta.crossunder(zscore, entry_z)

plotshape(cross_up_neg, title="Buy Signal", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down_pos, title="Sell Signal", shape="triangledown", location="abovebar", color="#ef5350", size="small")
bgcolor([("rgba(76,175,80,0.08)" if zscore[i] < -entry_z else None) for i in range(n)], title="OS Zone")
bgcolor([("rgba(244,67,54,0.08)" if zscore[i] > entry_z else None) for i in range(n)], title="OB Zone")
# --- Rich annotations ---
atr = ta.atr(high, low, close, 14)
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
