# Two Bar Reversal Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Target Multiplier", minval=1.0, maxval=5.0)
min_body = input.float(0.5, "Min Body Ratio", minval=0.3, maxval=0.8)

atr = ta.atr(high, low, close, atr_len)

body = np.abs(close - open)
candle_range = high - low
body_ratio = np.where(candle_range > 0, body / candle_range, 0)

# Bullish two-bar reversal: strong bearish bar followed by strong bullish bar
# Bar 2 close > Bar 1 open, Bar 2 open < Bar 1 close
bar1_bearish = close[-2] < open[-2] and body_ratio[-2] >= min_body
bar2_bullish = close[-1] > open[-1] and body_ratio[-1] >= min_body

bull_2bar = (bar1_bearish and bar2_bullish and
             close[-1] > open[-2] and open[-1] <= close[-2])

# Bearish two-bar reversal: strong bullish bar followed by strong bearish bar
bar1_bullish = close[-2] > open[-2] and body_ratio[-2] >= min_body
bar2_bearish = close[-1] < open[-1] and body_ratio[-1] >= min_body

bear_2bar = (bar1_bullish and bar2_bearish and
             close[-1] < open[-2] and open[-1] >= close[-2])

if bull_2bar:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long Exit", "Long",
                  stop=min(low[-1], low[-2]) - atr[-1] * 0.3,
                  limit=close[-1] + atr[-1] * atr_mult)

if bear_2bar:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short Exit", "Short",
                  stop=max(high[-1], high[-2]) + atr[-1] * 0.3,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(body_ratio, title="Body Ratio", color="blue")
hline(min_body, title="Min Body", color="gray")
plotshape(bull_2bar, title="Bull 2-Bar", style="triangleup", location="belowbar", color="green")
plotshape(bear_2bar, title="Bear 2-Bar", style="triangledown", location="abovebar", color="red")
