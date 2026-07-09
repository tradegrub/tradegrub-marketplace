from tg_scripting import *
import numpy as np

strategy("RSI MACD Combo", overlay=True)

# Inputs
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(70, "RSI Overbought", minval=50, maxval=90)
rsi_os = input.int(30, "RSI Oversold", minval=10, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=30)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
rsi = ta.rsi(close, rsi_len)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_sig)

# Conditions
macd_bull_cross = ta.crossover(macd_line, signal_line)
macd_bear_cross = ta.crossunder(macd_line, signal_line)

long_cond = (macd_bull_cross) & (rsi < rsi_ob) & (rsi > rsi_os)
short_cond = (macd_bear_cross) & (rsi > rsi_os) & (rsi < rsi_ob)

# Entries
for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(rsi, title="RSI", color="purple")
hline(rsi_ob, title="Overbought", color="red")
hline(rsi_os, title="Oversold", color="green")
plot(macd_line, title="MACD", color="blue")
plot(signal_line, title="Signal", color="orange")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 15

for i in range(macd_slow, n):
    if long_cond[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="MACD Cross\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
            label.new(x=i, y=float(low[i] - (high[i] - low[i]) * 0.5),
                      text="RSI: " + str(int(rsi[i])),
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#888888", size="small")

    elif short_cond[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="MACD Cross\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
            label.new(x=i, y=float(high[i] + (high[i] - low[i]) * 0.5),
                      text="RSI: " + str(int(rsi[i])),
                      style=label.style_none, color="rgba(0,0,0,0)",
                      textcolor="#888888", size="small")
