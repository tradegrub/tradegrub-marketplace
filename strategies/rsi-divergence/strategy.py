# RSI Divergence Mean Reversion
from tg_scripting import *

rsi_length = input.int(14, "RSI Length", minval=5, maxval=50)
oversold = input.int(30, "Oversold Level", minval=10, maxval=40)
overbought = input.int(70, "Overbought Level", minval=60, maxval=90)
lookback = input.int(5, "Divergence Lookback", minval=2, maxval=20)

rsi = ta.rsi(close, rsi_length)
price_low = ta.lowest(close, lookback)
price_high = ta.highest(close, lookback)
rsi_low = ta.lowest(rsi, lookback)
rsi_high = ta.highest(rsi, lookback)

# Bullish divergence: price makes lower low but RSI makes higher low
bullish_div = (close[-1] <= price_low[-1]) and (rsi[-1] > rsi_low[-2]) and (rsi[-1] < oversold)

# Bearish divergence: price makes higher high but RSI makes lower high
bearish_div = (close[-1] >= price_high[-1]) and (rsi[-1] < rsi_high[-2]) and (rsi[-1] > overbought)

if bullish_div:
    strategy.entry("Long", strategy.LONG)

if bearish_div:
    strategy.entry("Short", strategy.SHORT)

# Exit when RSI crosses midline
if rsi[-1] > 50 and rsi[-2] <= 50:
    strategy.close("Long")
if rsi[-1] < 50 and rsi[-2] >= 50:
    strategy.close("Short")

plot(rsi, title="RSI", color="purple")
hline(overbought, title="Overbought", color="red")
hline(oversold, title="Oversold", color="green")
hline(50, title="Midline", color="gray")

plotshape(bullish_div, title="Bull Div", style="triangleup", location="belowbar", color="green")
plotshape(bearish_div, title="Bear Div", style="triangledown", location="abovebar", color="red")
