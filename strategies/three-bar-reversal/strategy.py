# Three Bar Reversal Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Target Multiplier", minval=1.0, maxval=5.0)
trend_len = input.int(50, "Trend EMA Length", minval=20, maxval=200)

atr = ta.atr(high, low, close, atr_len)
trend_ema = ta.ema(close, trend_len)

# Three bar bullish reversal: bar1 bearish, bar2 lower low + lower close, bar3 bullish closes above bar1 high
bar1_bear = close[-3] < open[-3]
bar2_lower = low[-2] < low[-3] and close[-2] < close[-3]
bar3_bull_close = close[-1] > open[-1] and close[-1] > high[-3]

bull_3bar = bar1_bear and bar2_lower and bar3_bull_close

# Three bar bearish reversal: bar1 bullish, bar2 higher high + higher close, bar3 bearish closes below bar1 low
bar1_bull = close[-3] > open[-3]
bar2_higher = high[-2] > high[-3] and close[-2] > close[-3]
bar3_bear_close = close[-1] < open[-1] and close[-1] < low[-3]

bear_3bar = bar1_bull and bar2_higher and bar3_bear_close

if bull_3bar:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long Exit", "Long", stop=low[-2] - atr[-1] * 0.5,
                  limit=close[-1] + atr[-1] * atr_mult)

if bear_3bar:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short Exit", "Short", stop=high[-2] + atr[-1] * 0.5,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(trend_ema, title="Trend EMA", color="orange")
plotshape(bull_3bar, title="Bull 3-Bar", style="triangleup", location="belowbar", color="green")
plotshape(bear_3bar, title="Bear 3-Bar", style="triangledown", location="abovebar", color="red")
