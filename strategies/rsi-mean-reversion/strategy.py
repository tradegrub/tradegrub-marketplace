# RSI Mean Reversion Strategy
from tg_scripting import *
import numpy as np

indicator("RSI Mean Reversion", overlay=True)

length = input.int(14, "RSI Length", minval=2, maxval=100)
oversold = input.int(30, "Oversold Level", minval=5, maxval=50)
overbought = input.int(70, "Overbought Level", minval=50, maxval=95)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

rsi = ta.rsi(close, length)

buy = ta.crossover(rsi, oversold)
sell = ta.crossunder(rsi, overbought)
for i in range(len(close)):
    strategy.set_bar_index(i)
    if buy[i]:
        strategy.entry("Long", strategy.LONG)
    if sell[i]:
        strategy.close("Long")

plot(rsi, title="RSI", color="purple")
hline(overbought, title="Overbought", color="red")
hline(oversold, title="Oversold", color="green")

plotshape(buy.tolist(), title="Buy", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(sell.tolist(), title="Exit", style="xcross", location="abovebar", color="#ff9800", size="small")

# Oversold/overbought zone shading on price panel
_n_bg = len(close)
_zone_bg = [
    ("rgba(0,230,118,0.10)" if rsi[i] <= oversold else
     ("rgba(239,83,80,0.10)" if rsi[i] >= overbought else None))
    for i in range(_n_bg)
]
bgcolor(_zone_bg, title="RSI Zone")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 15

for i in range(length, n):
    if buy[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Oversold\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
            label.new(x=i, y=float(low[i] - (high[i] - low[i]) * 0.5),
                      text="RSI: " + str(int(rsi[i])),
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#888888", size="small")

    elif sell[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Overbought\nEXIT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
            label.new(x=i, y=float(high[i] + (high[i] - low[i]) * 0.5),
                      text="RSI: " + str(int(rsi[i])),
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#888888", size="small")
