from tg_scripting import *

# Inputs
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(70, "RSI Overbought", minval=50, maxval=90)
rsi_os = input.int(30, "RSI Oversold", minval=10, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=30)

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
