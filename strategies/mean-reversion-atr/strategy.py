# ATR-Based Mean Reversion from SMA
from tg_scripting import *
import numpy as np

indicator("Mean Reversion ATR", overlay=True)

sma_length = input.int(50, "SMA Length", minval=10, maxval=200)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.5, "ATR Multiplier", minval=1.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

sma = ta.sma(close, sma_length)
atr = ta.atr(high, low, close, atr_length)

upper_band = sma + atr * atr_mult
lower_band = sma - atr * atr_mult

# Enter when price reverts from ATR extremes
n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if ta.crossover(close, lower_band)[i]:
        strategy.entry("Long", strategy.LONG)

    if ta.crossunder(close, upper_band)[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit at SMA
    if ta.crossunder(close, sma)[i]:
        strategy.close("Long")
    if ta.crossover(close, sma)[i]:
        strategy.close("Short")

plot(sma, title="SMA", color="blue")
plot(upper_band, title="Upper ATR Band", color="red")
plot(lower_band, title="Lower ATR Band", color="green")
fill("Upper ATR Band", "Lower ATR Band", color="rgba(33, 150, 243, 0.06)")

# --- Rich annotations ---
cross_up_lower = ta.crossover(close, lower_band)
cross_down_upper = ta.crossunder(close, upper_band)

plotshape(cross_up_lower, title="Buy Signal", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down_upper, title="Sell Signal", style="triangledown", location="abovebar", color="#ef5350", size="small")

bgcolor_vals = [
    ("rgba(76,175,80,0.08)" if float(close[i]) <= float(lower_band[i]) else
     "rgba(244,67,54,0.08)" if float(close[i]) >= float(upper_band[i]) else None)
    for i in range(n)
]
bgcolor(bgcolor_vals)

last_signal_idx = -100
cooldown = 20

for i in range(sma_length, n):
    if cross_up_lower[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="LONG\nMean Revert",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            tp_price = float(sma[i])
            sl_price = float(lower_band[i] - atr[i])
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="TP (SMA)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down_upper[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="SHORT\nMean Revert",
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            tp_price = float(sma[i])
            sl_price = float(upper_band[i] + atr[i])
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="TP (SMA)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
