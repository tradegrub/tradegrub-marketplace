from tg_scripting import *
import numpy as np

strategy("MA RSI BB", overlay=True)

# Inputs
ma_len = input.int(50, "Moving Average Length", minval=5, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(70, "RSI Overbought", minval=50, maxval=90)
rsi_os = input.int(30, "RSI Oversold", minval=10, maxval=50)
bb_len = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
ma = ta.sma(close, ma_len)
rsi = ta.rsi(close, rsi_len)
bb_upper, bb_basis, bb_lower = ta.bb(close, bb_len, bb_mult)
atr = ta.atr(high, low, close, 14)

# Long: price above MA (uptrend), RSI not overbought, price touches lower BB (pullback)
long_cond = (close > ma) & (rsi < rsi_ob) & (close <= bb_lower)
# Short: price below MA (downtrend), RSI not oversold, price touches upper BB (pullback)
short_cond = (close < ma) & (rsi > rsi_os) & (close >= bb_upper)

n = len(close)
last_signal_idx = -100
cooldown = 20

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(low[i]),
                    text="LONG\nBB Pullback",
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
                    text="SHORT\nBB Pullback",
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
plot(bb_basis, title="BB Basis", color="gray")
plot(ma, title="SMA", color="blue")
fill(p_upper, p_lower, color="rgba(100, 100, 255, 0.1)")
