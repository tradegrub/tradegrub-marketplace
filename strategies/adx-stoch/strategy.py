from tg_scripting import *
import numpy as np

strategy("ADX Stoch", overlay=True)

# Inputs
adx_dilen = input.int(14, "DI Length", minval=2, maxval=50)
adx_adxlen = input.int(14, "ADX Length", minval=2, maxval=50)
adx_thresh = input.int(20, "ADX Threshold", minval=10, maxval=50)
stoch_len = input.int(14, "Stochastic Length", minval=2, maxval=50)
stoch_smooth = input.int(3, "Stochastic Smoothing", minval=1, maxval=10)
stoch_ob = input.int(80, "Stochastic Overbought", minval=60, maxval=95)
stoch_os = input.int(20, "Stochastic Oversold", minval=5, maxval=40)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
plus_di, minus_di, adx_val = ta.dmi(high, low, close, adx_dilen)
stoch_k, _ = ta.stoch(high, low, close, stoch_len, 3, 3)
k_smooth = ta.sma(stoch_k, stoch_smooth)
d_line = ta.sma(k_smooth, stoch_smooth)

# ADX trending + DI direction + Stochastic entry
trending = adx_val > adx_thresh
bullish_trend = trending & (plus_di > minus_di)
bearish_trend = trending & (minus_di > plus_di)

stoch_cross_up = ta.crossover(k_smooth, d_line)
stoch_cross_down = ta.crossunder(k_smooth, d_line)

long_cond = bullish_trend & stoch_cross_up & (k_smooth < stoch_ob)
short_cond = bearish_trend & stoch_cross_down & (k_smooth > stoch_os)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(adx_val, title="ADX", color="blue")
hline(adx_thresh, title="ADX Threshold", color="gray")
plot(k_smooth, title="Stoch %K", color="green")
plot(d_line, title="Stoch %D", color="red")
hline(stoch_ob, title="Overbought", color="red")
hline(stoch_os, title="Oversold", color="green")

# --- Rich annotations ---
atr = ta.atr(high, low, close, 14)
n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30

for i in range(1, n):
    if long_cond[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
            label.new(x=i, y=float(low[i] - atr[i] * 0.5), text="Stoch Cross Up",
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#42a5f5", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2)
            tp_price = float(close[i] + atr[i] * 3)
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

    elif short_cond[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
            label.new(x=i, y=float(high[i] + atr[i] * 0.5), text="Stoch Cross Down",
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#ef5350", size="small")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * 2)
            tp_price = float(close[i] - atr[i] * 3)
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
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
