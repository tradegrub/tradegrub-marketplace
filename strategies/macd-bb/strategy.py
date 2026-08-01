from tg_scripting import *
import numpy as np

indicator("MACD BB", overlay=True)

# Inputs
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=30)
bb_len = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_sig)
bb_upper, bb_basis, bb_lower = ta.bb(close, bb_len, bb_mult)
atr = ta.atr(high, low, close, 14)

# MACD crossover at BB extremes
macd_bull = ta.crossover(macd_line, signal_line)
macd_bear = ta.crossunder(macd_line, signal_line)

# Long: MACD bullish crossover when price is near or below lower band
long_cond = macd_bull & (close <= bb_basis)
# Short: MACD bearish crossover when price is near or above upper band
short_cond = macd_bear & (close >= bb_basis)

n = len(close)
last_signal_idx = -100
cooldown = 20

for i in range(len(close)):
    strategy.set_bar_index(i)
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(low[i]),
                    text="LONG\nMACD Cross",
                    style=label.style_label_up,
                    color="#00e676",
                    textcolor="#000000",
                    size="normal"
                )
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] - atr[i] * 2.0)
                tp_price = float(bb_upper[i])
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
                label.new(x=i + 2, y=tp_price, text="TP (Upper BB)",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                        border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(high[i]),
                    text="SHORT\nMACD Cross",
                    style=label.style_label_down,
                    color="#ef5350",
                    textcolor="#ffffff",
                    size="normal"
                )
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] + atr[i] * 2.0)
                tp_price = float(bb_lower[i])
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
                label.new(x=i + 2, y=tp_price, text="TP (Lower BB)",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                        border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

# Plots
p_upper = plot(bb_upper, title="BB Upper", color="red")
p_lower = plot(bb_lower, title="BB Lower", color="green")
plot(bb_basis, title="BB Middle", color="gray")
fill(p_upper, p_lower, color="rgba(150, 150, 255, 0.1)")
plot(macd_line, title="MACD Line", color="blue")
plot(signal_line, title="Signal Line", color="orange")
hline(0, title="Zero Line", color="gray", linestyle="dashed")

plotshape(long_cond, title="Long Entry", shape="triangleup", location="belowbar", color="green")
plotshape(short_cond, title="Short Entry", shape="triangledown", location="abovebar", color="red")
