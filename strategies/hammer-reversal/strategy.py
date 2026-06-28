# Hammer Reversal Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
wick_ratio = input.float(2.0, "Min Wick-to-Body Ratio", minval=1.5, maxval=5.0)
trend_len = input.int(20, "Trend SMA Length", minval=10, maxval=50)

atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, trend_len)

body = np.abs(close - open)
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low
candle_range = high - low

# Hammer: small body at top, long lower wick, in downtrend
is_hammer = ((lower_wick[-1] > body[-1] * wick_ratio) and
             (upper_wick[-1] < body[-1] * 0.5) and
             (body[-1] > 0) and
             (close[-1] < trend_sma[-1]))

# Shooting star: small body at bottom, long upper wick, in uptrend
is_shooting_star = ((upper_wick[-1] > body[-1] * wick_ratio) and
                    (lower_wick[-1] < body[-1] * 0.5) and
                    (body[-1] > 0) and
                    (close[-1] > trend_sma[-1]))

if is_hammer:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long SL", "Long", stop=low[-1] - atr[-1] * 0.5,
                  limit=close[-1] + atr[-1] * atr_mult)

if is_shooting_star:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short SL", "Short", stop=high[-1] + atr[-1] * 0.5,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(trend_sma, title="Trend SMA", color="orange")
plotshape(is_hammer, title="Hammer", style="triangleup", location="belowbar", color="green")
plotshape(is_shooting_star, title="Shooting Star", style="triangledown", location="abovebar", color="red")
