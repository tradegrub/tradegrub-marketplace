from tg_scripting import *
import numpy as np

indicator("Trend Exhaustion", overlay=True)

ma_len = input.int(50, "MA Length", minval=10, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
rsi_upper = input.float(75.0, "RSI Overbought", minval=65.0, maxval=90.0)
rsi_lower = input.float(25.0, "RSI Oversold", minval=10.0, maxval=35.0)
dist_mult = input.float(2.0, "Distance Multiplier", minval=1.0, maxval=4.0)
vol_mult = input.float(1.8, "Volume Spike Mult", minval=1.2, maxval=3.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
use_volume = input.bool(True, "Require Volume Climax")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

ma = ta.ema(close, ma_len)
rsi = ta.rsi(close, rsi_len)
atr = ta.atr(high, low, close, atr_len)
vol_ma = ta.sma(volume, 20)

distance = (close - ma) / atr
vol_spike = volume > (vol_ma * vol_mult)

bear_exhaustion = (distance > dist_mult) & (rsi > rsi_upper)
bull_exhaustion = (distance < -dist_mult) & (rsi < rsi_lower)

if use_volume:
    bear_exhaustion = bear_exhaustion & vol_spike
    bull_exhaustion = bull_exhaustion & vol_spike

plot(ma, title="EMA Baseline", color="#ff9800", linewidth=2)
plot(distance, title="MA Distance", color="white")
hline(dist_mult, title="Upper Threshold", color="red", linestyle="dashed")
hline(-dist_mult, title="Lower Threshold", color="green", linestyle="dashed")
hline(0, title="Zero", color="gray", linestyle="dotted")

plotshape(bear_exhaustion, title="Bearish Exhaustion", shape="triangledown", location="abovebar", color="red", size="small")
plotshape(bull_exhaustion, title="Bullish Exhaustion", shape="triangleup", location="belowbar", color="green", size="small")

bgcolor(bear_exhaustion, color="rgba(255,0,0,0.1)")
bgcolor(bull_exhaustion, color="rgba(0,255,0,0.1)")

n = len(close)
last_signal_idx = -100

for i in range(len(close)):
    strategy.set_bar_index(i)
    if bull_exhaustion[i]:
        strategy.entry("Long", strategy.LONG)
    elif bear_exhaustion[i]:
        strategy.entry("Short", strategy.SHORT)

    if strategy.position_size > 0 and ta.crossunder(close, ma)[i]:
        strategy.close("Long")
    elif strategy.position_size < 0 and ta.crossover(close, ma)[i]:
        strategy.close("Short")

    # --- Rich annotations ---
    if bull_exhaustion[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Exhaustion\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
            if vol_spike[i]:
                label.new(x=i, y=float(low[i] - atr[i] * 0.5), text="Vol Climax",
                          style=label.style_none, color="rgba(0,0,0,0)",
                          textcolor="#42a5f5", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2)
            tp_price = float(ma[i])
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
            label.new(x=i + 2, y=tp_price, text="TP (MA)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=max(tp_price, entry_price), right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif bear_exhaustion[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Exhaustion\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
            if vol_spike[i]:
                label.new(x=i, y=float(high[i] + atr[i] * 0.5), text="Vol Climax",
                          style=label.style_none, color="rgba(0,0,0,0)",
                          textcolor="#42a5f5", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * 2)
            tp_price = float(ma[i])
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
            label.new(x=i + 2, y=tp_price, text="TP (MA)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=min(tp_price, entry_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
