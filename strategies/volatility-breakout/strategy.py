# Volatility Breakout (Bollinger Band Width Expansion)
from tg_scripting import *

indicator("Volatility Breakout", overlay=True)

bb_length = input.int(20, "BB Length", minval=10, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=1.0, maxval=4.0)
squeeze_pctile = input.float(20.0, "Squeeze Percentile", minval=5.0, maxval=50.0)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_sl_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=4.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Bollinger Bands and width
upper, basis, lower = ta.bb(close, bb_length, bb_mult)
bbw = ta.bbw(close, bb_length, bb_mult)
atr = ta.atr(high, low, close, atr_length)

# Detect squeeze: BBW below its own percentile threshold
bbw_min = ta.lowest(bbw, 100)
bbw_max = ta.highest(bbw, 100)
bbw_range = bbw_max - bbw_min
bbw_threshold = bbw_min + bbw_range * (squeeze_pctile / 100.0)
in_squeeze = bbw < bbw_threshold

# Breakout from squeeze
long_signal = ta.crossover(close, upper) & in_squeeze
short_signal = ta.crossunder(close, lower) & in_squeeze

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when price returns inside bands
if ta.crossunder(close, basis)[-1]:
    strategy.close("Long")

if ta.crossover(close, basis)[-1]:
    strategy.close("Short")

strategy.exit("Long SL", from_entry="Long", trail_offset=atr[-1] * atr_sl_mult)
strategy.exit("Short SL", from_entry="Short", trail_offset=atr[-1] * atr_sl_mult)

p1 = plot(upper, title="BB Upper", color="blue")
p2 = plot(lower, title="BB Lower", color="blue")
plot(basis, title="BB Basis", color="gray")
fill(p1, p2, color="rgba(33, 150, 243, 0.06)")

bgcolor(in_squeeze, color="rgba(255, 235, 59, 0.1)")
plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
squeeze_label_placed = False

for i in range(bb_length, n):
    if show_labels and not squeeze_label_placed and in_squeeze[i]:
        squeeze_label_placed = True
        label.new(x=i, y=float(upper[i]), text="Squeeze",
                  style=label.style_label_down, color="rgba(255,235,59,0.3)",
                  textcolor="#fdd835", size="normal")

    if not in_squeeze[i]:
        squeeze_label_placed = False

    if long_signal[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_sl_mult)
            tp_price = float(upper[i] + (upper[i] - basis[i]))
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_signal[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="BREAKOUT\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_sl_mult)
            tp_price = float(lower[i] - (basis[i] - lower[i]))
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
