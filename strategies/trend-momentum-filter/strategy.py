from tg_scripting import *
import numpy as np

indicator("Trend Momentum Filter", overlay=True)

# Inputs
adx_dilen = input.int(14, "DI Length", minval=2, maxval=50)
adx_adxlen = input.int(14, "ADX Length", minval=2, maxval=50)
adx_thresh = input.int(25, "ADX Trend Threshold", minval=10, maxval=50)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(65, "RSI Long Entry Above", minval=50, maxval=80)
rsi_os = input.int(35, "RSI Short Entry Below", minval=20, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
plus_di, minus_di, adx_val = ta.dmi(high, low, close, adx_dilen)
rsi = ta.rsi(close, rsi_len)

# Conditions - ADX confirms trend, DI gives direction, RSI gives momentum
trending = adx_val > adx_thresh
long_cond = trending & (plus_di > minus_di) & (rsi > rsi_ob)
short_cond = trending & (minus_di > plus_di) & (rsi < rsi_os)

n = len(close)
atr = ta.atr(high, low, close, adx_dilen)
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
            label.new(x=i, y=float(low[i]), text="LONG\nADX+RSI",
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
            label.new(x=i, y=float(high[i]), text="SHORT\nADX+RSI",
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
plot(adx_val, title="ADX", color="blue")
plot(plus_di, title="+DI", color="green")
plot(minus_di, title="-DI", color="red")
hline(adx_thresh, title="Trend Threshold", color="gray")
