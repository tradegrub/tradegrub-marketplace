# Price vs RSI Divergence Strategy
from tg_scripting import *
import numpy as np

indicator("Momentum Divergence", overlay=True)

rsi_length = input.int(14, "RSI Length", minval=2, maxval=50)
lookback = input.int(20, "Divergence Lookback", minval=5, maxval=50)
ob_level = input.int(70, "Overbought", minval=60, maxval=90)
os_level = input.int(30, "Oversold", minval=10, maxval=40)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

rsi = ta.rsi(close, rsi_length)
atr = ta.atr(high, low, close, 14)

price_low = ta.lowest(close, lookback)
rsi_low = ta.lowest(rsi, lookback)

price_high = ta.highest(close, lookback)
rsi_high = ta.highest(rsi, lookback)

# Bullish divergence: price makes new low but RSI makes higher low
prev_rsi_low = np.roll(rsi_low, 1)
bullish_div = (close <= price_low) & (rsi > prev_rsi_low) & (rsi < os_level)

# Bearish divergence: price makes new high but RSI makes lower high
prev_rsi_high = np.roll(rsi_high, 1)
bearish_div = (close >= price_high) & (rsi < prev_rsi_high) & (rsi > ob_level)

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if bullish_div[i]:
        strategy.entry("Long", strategy.LONG)

    if bearish_div[i]:
        strategy.close("Long")

plot(rsi, title="RSI", color="purple")
hline(ob_level, title="Overbought", color="red")
hline(os_level, title="Oversold", color="green")
hline(50, title="Midline", color="gray")

# Entry/exit markers
plotshape(bullish_div, title="Bullish Divergence", style="triangleup", location="belowbar", color="#00e676")
plotshape(bearish_div, title="Bearish Divergence / Exit", style="xcross", location="absolute", color="#ff9800")

# Overbought/oversold zone shading
ob_zone = np.array([rsi[i] > ob_level for i in range(n)])
os_zone = np.array([rsi[i] < os_level for i in range(n)])
bgcolor(ob_zone, color="rgba(244,67,54,0.12)")
bgcolor(os_zone, color="rgba(76,175,80,0.12)")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 20

for i in range(lookback + 1, n):
    is_bull_div = (close[i] <= price_low[i]) and (rsi[i] > rsi_low[i - 1]) and (rsi[i] < os_level)
    is_bear_div = (close[i] >= price_high[i]) and (rsi[i] < rsi_high[i - 1]) and (rsi[i] > ob_level)

    if is_bull_div and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="Bullish Div",
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
            # Draw divergence line on price
            div_start = max(0, i - lookback)
            line.new(x1=div_start, y1=float(close[div_start]), x2=i, y2=float(close[i]),
                     color="#00e676", width=2, style=line.style_dashed)

        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2.0)
            tp_price = float(close[i] + atr[i] * 4.0)
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

    elif is_bear_div and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="Bearish Div",
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
            div_start = max(0, i - lookback)
            line.new(x1=div_start, y1=float(close[div_start]), x2=i, y2=float(close[i]),
                     color="#ef5350", width=2, style=line.style_dashed)
