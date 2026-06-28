# Opening Range Breakout Strategy
from tg_scripting import *

or_bars = input.int(5, "Opening Range Bars", minval=1, maxval=30)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_tp_mult = input.float(2.0, "ATR Take Profit Multiplier", minval=1.0, maxval=5.0)
atr_sl_mult = input.float(1.0, "ATR Stop Loss Multiplier", minval=0.5, maxval=3.0)

# Calculate opening range as highest/lowest of first N bars
or_high = ta.highest(high, or_bars)
or_low = ta.lowest(low, or_bars)
or_mid = (or_high + or_low) / 2
atr = ta.atr(high, low, close, atr_length)

# Breakout above/below the opening range
long_signal = ta.crossover(close, or_high)
short_signal = ta.crossunder(close, or_low)

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# Take profit and stop loss based on ATR
strategy.exit("Long TP/SL", from_entry="Long",
              limit=close[-1] + atr[-1] * atr_tp_mult,
              stop=close[-1] - atr[-1] * atr_sl_mult)
strategy.exit("Short TP/SL", from_entry="Short",
              limit=close[-1] - atr[-1] * atr_tp_mult,
              stop=close[-1] + atr[-1] * atr_sl_mult)

# Exit at midline as fallback
if ta.crossunder(close, or_mid)[-1]:
    strategy.close("Long")

if ta.crossover(close, or_mid)[-1]:
    strategy.close("Short")

p1 = plot(or_high, title="OR High", color="green")
p2 = plot(or_low, title="OR Low", color="red")
plot(or_mid, title="OR Mid", color="orange")
fill(p1, p2, color="rgba(255, 152, 0, 0.06)")

plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")
