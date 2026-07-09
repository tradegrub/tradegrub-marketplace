# Inside Bar Breakout Strategy
from tg_scripting import *
import numpy as np

strategy("Inside Bar Breakout", overlay=True)

atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_tp_mult = input.float(2.0, "ATR Take Profit Multiplier", minval=1.0, maxval=5.0)
atr_sl_mult = input.float(0.5, "ATR Stop Buffer", minval=0.1, maxval=2.0)
require_trend = input.bool(True, "Require Trend Alignment")
ma_length = input.int(50, "Trend MA Length", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_length)
trend_ma = ta.sma(close, ma_length)

# Detect inside bars: current bar's range is entirely within prior bar's range
prev_high = np.roll(high, 1)
prev_low = np.roll(low, 1)
inside_bar = (high <= prev_high) & (low >= prev_low)

# Breakout of mother bar (previous bar) range
long_signal = ta.crossover(close, prev_high) & np.roll(inside_bar, 1)
short_signal = ta.crossunder(close, prev_low) & np.roll(inside_bar, 1)

# Optional trend filter
if require_trend:
    long_signal = long_signal & (close > trend_ma)
    short_signal = short_signal & (close < trend_ma)

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# TP and SL based on ATR
strategy.exit("Long TP/SL", from_entry="Long",
              limit=close[-1] + atr[-1] * atr_tp_mult,
              stop=prev_low[-1] - atr[-1] * atr_sl_mult)
strategy.exit("Short TP/SL", from_entry="Short",
              limit=close[-1] - atr[-1] * atr_tp_mult,
              stop=prev_high[-1] + atr[-1] * atr_sl_mult)

plot(trend_ma, title="Trend MA", color="blue")
bgcolor(inside_bar, color="rgba(156, 39, 176, 0.1)")
plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if long_signal[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Inside Bar\nBREAKOUT",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
            if inside_bar[i - 1]:
                label.new(x=i - 1, y=float(high[i - 1]),
                          text="Mother Bar",
                          style=label.style_none, color="rgba(0,0,0,0)",
                          textcolor="#888888", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(prev_low[i] - atr[i] * atr_sl_mult)
            tp_price = float(close[i] + atr[i] * atr_tp_mult)
            end_bar = min(i + 20, n - 1)
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

    elif short_signal[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Inside Bar\nBREAKDOWN",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(prev_high[i] + atr[i] * atr_sl_mult)
            tp_price = float(close[i] - atr[i] * atr_tp_mult)
            end_bar = min(i + 20, n - 1)
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
