# Moving Average Envelope Breakout Strategy
from tg_scripting import *
import numpy as np

indicator("Moving Avg Envelope", overlay=True)

length = input.int(20, "MA Length", minval=5, maxval=200)
pct = input.float(2.5, "Envelope Percent", minval=0.5, maxval=10.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

basis = ta.sma(close, length)
upper = basis * (1 + pct / 100)
lower = basis * (1 - pct / 100)
atr = ta.atr(high, low, close, 14)

# Enter long on upper envelope breakout
n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if ta.crossover(close, upper)[i]:
        strategy.entry("Long", strategy.LONG)

    # Enter short on lower envelope breakdown
    if ta.crossunder(close, lower)[i]:
        strategy.entry("Short", strategy.SHORT)

    # Exit at basis
    if ta.crossunder(close, basis)[i]:
        strategy.close("Long")
    if ta.crossover(close, basis)[i]:
        strategy.close("Short")

p1 = plot(upper, title="Upper Envelope", color="green")
p2 = plot(lower, title="Lower Envelope", color="red")
plot(basis, title="MA Basis", color="blue")
fill(p1, p2, color="rgba(100, 181, 246, 0.08)")

# --- Entry / exit markers ---
_cross_up = ta.crossover(close, upper)
_cross_down = ta.crossunder(close, lower)
_exit_long = ta.crossunder(close, basis)
_exit_short = ta.crossover(close, basis)
plotshape(_cross_up, title="Long Entry", style="triangleup", location="belowbar", color="green")
plotshape(_cross_down, title="Short Entry", style="triangledown", location="abovebar", color="red")
plotshape(_exit_long, title="Exit Long", style="xcross", location="abovebar", color="orange")
plotshape(_exit_short, title="Exit Short", style="xcross", location="belowbar", color="orange")

# --- Rich annotations ---
n = len(close)
cross_up = ta.crossover(close, upper)
cross_down = ta.crossunder(close, lower)
last_signal_idx = -100
cooldown = 20

for i in range(length, n):
    if cross_up[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="LONG\nBreakout",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(basis[i])
            tp_price = float(close[i] + atr[i] * 3.0)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop (Basis)",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif cross_down[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="SHORT\nBreakdown",
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(basis[i])
            tp_price = float(close[i] - atr[i] * 3.0)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop (Basis)",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
