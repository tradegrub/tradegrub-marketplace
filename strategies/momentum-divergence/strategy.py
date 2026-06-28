# Price vs RSI Divergence Strategy
from tg_scripting import *

rsi_length = input.int(14, "RSI Length", minval=2, maxval=50)
lookback = input.int(20, "Divergence Lookback", minval=5, maxval=50)
ob_level = input.int(70, "Overbought", minval=60, maxval=90)
os_level = input.int(30, "Oversold", minval=10, maxval=40)

rsi = ta.rsi(close, rsi_length)

price_low = ta.lowest(close, lookback)
rsi_low = ta.lowest(rsi, lookback)

price_high = ta.highest(close, lookback)
rsi_high = ta.highest(rsi, lookback)

# Bullish divergence: price makes new low but RSI makes higher low
bullish_div = close[-1] <= price_low[-1] and rsi[-1] > rsi_low[-2] and rsi[-1] < os_level

# Bearish divergence: price makes new high but RSI makes lower high
bearish_div = close[-1] >= price_high[-1] and rsi[-1] < rsi_high[-2] and rsi[-1] > ob_level

if bullish_div:
    strategy.entry("Long", strategy.LONG)

if bearish_div:
    strategy.close("Long")

plot(rsi, title="RSI", color="purple")
hline(ob_level, title="Overbought", color="red")
hline(os_level, title="Oversold", color="green")
hline(50, title="Midline", color="gray")
