# Pivot Point Breakout Strategy
from tg_scripting import *
import numpy as np

strategy("Pivot Breakout", overlay=True)

lookback = input.int(5, "Pivot Lookback", minval=2, maxval=20)
confirm_bars = input.int(2, "Confirmation Bars", minval=1, maxval=5)
use_volume = input.bool(True, "Require Volume Confirmation")
vol_mult = input.float(1.5, "Volume Multiplier", minval=1.0, maxval=3.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Find pivot highs and lows using highest/lowest
pivot_high = ta.highest(high, lookback)
pivot_low = ta.lowest(low, lookback)

# Volume filter
avg_vol = ta.sma(volume, 20)
vol_confirm = volume > avg_vol * vol_mult if use_volume else np.ones(len(close), dtype=bool)

# Breakout above pivot high
long_signal = (close > pivot_high) & vol_confirm
short_signal = (close < pivot_low) & vol_confirm

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when price returns to mid range
mid = (pivot_high + pivot_low) / 2
if ta.crossunder(close, mid)[-1]:
    strategy.close("Long")

if ta.crossover(close, mid)[-1]:
    strategy.close("Short")

p1 = plot(pivot_high, title="Pivot High", color="green")
p2 = plot(pivot_low, title="Pivot Low", color="red")
plot(mid, title="Mid Line", color="orange")
fill(p1, p2, color="rgba(100, 100, 200, 0.06)")

plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 20
cooldown = lookback * 3

for i in range(lookback, n):
    if long_signal[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(pivot_low[i])
            tp_price = float(close[i] + (close[i] - pivot_low[i]))
            end_bar = min(i + exit_bars, n - 1)
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
            sl_price = float(pivot_high[i])
            tp_price = float(close[i] - (pivot_high[i] - close[i]))
            end_bar = min(i + exit_bars, n - 1)
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
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")
