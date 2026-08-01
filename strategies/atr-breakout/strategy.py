# ATR Range Expansion Breakout
from tg_scripting import *
import numpy as np

indicator("ATR Breakout", overlay=True)

atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Breakout Multiplier", minval=0.5, maxval=4.0)
ma_length = input.int(20, "MA Length", minval=5, maxval=100)
exit_mult = input.float(1.0, "ATR Exit Multiplier", minval=0.5, maxval=3.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_length)
basis = ta.sma(close, ma_length)

# Breakout levels based on ATR expansion from moving average
upper_band = basis + atr * atr_mult
lower_band = basis - atr * atr_mult

# Entry on ATR expansion breakout
long_signal = ta.crossover(close, upper_band)
short_signal = ta.crossunder(close, lower_band)

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if long_signal[i]:
        strategy.entry("Long", strategy.LONG)

    if short_signal[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit using tighter ATR band
    exit_upper = basis + atr * exit_mult
    exit_lower = basis - atr * exit_mult

    if ta.crossunder(close, exit_lower)[i]:
        strategy.close("Long")

    if ta.crossover(close, exit_upper)[i]:
        strategy.close("Short")

p1 = plot(upper_band, title="Upper ATR Band", color="green")
p2 = plot(lower_band, title="Lower ATR Band", color="red")
plot(basis, title="Basis MA", color="blue")
fill(p1, p2, color="rgba(33, 150, 243, 0.06)")

plotshape(long_signal, title="Long Entry", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Entry", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars_ann = 30

for i in range(1, n):
    if long_signal[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(exit_lower[i])
            tp_price = float(close[i] + (close[i] - exit_lower[i]) * 2)
            end_bar = min(i + exit_bars_ann, n - 1)
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
            label.new(x=i, y=float(high[i]), text="BREAKOUT\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(exit_upper[i])
            tp_price = float(close[i] - (exit_upper[i] - close[i]) * 2)
            end_bar = min(i + exit_bars_ann, n - 1)
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
