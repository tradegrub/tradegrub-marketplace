from tg_scripting import *
import numpy as np

strategy("Triple Screen", overlay=True)

# Inputs - Elder Triple Screen
ema_len = input.int(13, "Trend EMA Length", minval=5, maxval=100)
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=30)
stoch_len = input.int(14, "Stochastic Length", minval=2, maxval=50)
stoch_ob = input.int(80, "Stochastic Overbought", minval=60, maxval=95)
stoch_os = input.int(20, "Stochastic Oversold", minval=5, maxval=40)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Screen 1: Trend (EMA slope)
ema_trend = ta.ema(close, ema_len)
ema_slope = ta.change(ema_trend, 1)
uptrend = ema_slope > 0
downtrend = ema_slope < 0

# Screen 2: Momentum (MACD histogram)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_sig)
hist_rising = ta.change(hist, 1) > 0
hist_falling = ta.change(hist, 1) < 0

# Screen 3: Entry (Stochastic)
stoch_k, _ = ta.stoch(high, low, close, stoch_len, 3, 3)
stoch_smooth = ta.sma(stoch_k, 3)

# Triple screen logic
long_cond = uptrend & hist_rising & (stoch_smooth < stoch_os)
short_cond = downtrend & hist_falling & (stoch_smooth > stoch_ob)

n = len(close)
atr = ta.atr(high, low, close, ema_len)
last_signal_idx = -100

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

    # --- Rich annotations ---
    if long_cond[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG\nTriple Screen",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2)
            tp_price = float(close[i] + atr[i] * 3)
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

    elif short_cond[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT\nTriple Screen",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * 2)
            tp_price = float(close[i] - atr[i] * 3)
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

# Plots
plot(ema_trend, title="Trend EMA", color="blue")
plot(hist, title="MACD Histogram", color="teal")
plot(stoch_smooth, title="Stochastic %K", color="purple")
hline(stoch_ob, title="Stoch OB", color="red")
hline(stoch_os, title="Stoch OS", color="green")
