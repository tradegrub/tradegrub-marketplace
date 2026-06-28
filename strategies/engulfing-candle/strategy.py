# Engulfing Candle Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
min_body_ratio = input.float(0.6, "Min Body Ratio", minval=0.3, maxval=0.9)

atr = ta.atr(high, low, close, atr_len)

body = np.abs(close - open)
candle_range = high - low
body_ratio = np.where(candle_range > 0, body / candle_range, 0)

prev_body = np.abs(close[-2] - open[-2])
curr_body = np.abs(close[-1] - open[-1])

prev_bearish = close[-2] < open[-2]
prev_bullish = close[-2] > open[-2]
curr_bullish = close[-1] > open[-1]
curr_bearish = close[-1] < open[-1]

# Bullish engulfing: prev bearish, curr bullish, curr body engulfs prev body
bullish_engulf = (prev_bearish and curr_bullish and
                  close[-1] > open[-2] and open[-1] < close[-2] and
                  body_ratio[-1] >= min_body_ratio)

# Bearish engulfing: prev bullish, curr bearish, curr body engulfs prev body
bearish_engulf = (prev_bullish and curr_bearish and
                  close[-1] < open[-2] and open[-1] > close[-2] and
                  body_ratio[-1] >= min_body_ratio)

if bullish_engulf:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long SL", "Long", stop=close[-1] - atr[-1] * atr_mult)

if bearish_engulf:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short SL", "Short", stop=close[-1] + atr[-1] * atr_mult)

plot(body_ratio, title="Body Ratio", color="blue")
hline(min_body_ratio, title="Min Ratio", color="gray")
plotshape(bullish_engulf, title="Bull Engulf", style="triangleup", location="belowbar", color="green")
plotshape(bearish_engulf, title="Bear Engulf", style="triangledown", location="abovebar", color="red")
