# Pin Bar Reversal Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Target Multiplier", minval=1.0, maxval=5.0)
nose_ratio = input.float(0.33, "Max Nose Ratio", minval=0.1, maxval=0.5)
tail_ratio = input.float(0.6, "Min Tail Ratio", minval=0.4, maxval=0.8)
trend_len = input.int(20, "Trend SMA Length", minval=10, maxval=50)

atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, trend_len)

body = np.abs(close - open)
candle_range = high - low
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low

body_ratio = np.where(candle_range > 0, body / candle_range, 1.0)
upper_ratio = np.where(candle_range > 0, upper_wick / candle_range, 0)
lower_ratio = np.where(candle_range > 0, lower_wick / candle_range, 0)

# Bullish pin bar: long lower tail, small body near top
bull_pin = (body_ratio[-1] <= nose_ratio and
            lower_ratio[-1] >= tail_ratio and
            close[-1] < trend_sma[-1])

# Bearish pin bar: long upper tail, small body near bottom
bear_pin = (body_ratio[-1] <= nose_ratio and
            upper_ratio[-1] >= tail_ratio and
            close[-1] > trend_sma[-1])

if bull_pin:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long Exit", "Long", stop=low[-1] - atr[-1] * 0.3,
                  limit=close[-1] + atr[-1] * atr_mult)

if bear_pin:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short Exit", "Short", stop=high[-1] + atr[-1] * 0.3,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(trend_sma, title="Trend SMA", color="orange")
plot(body_ratio, title="Body Ratio", color="blue")
plotshape(bull_pin, title="Bull Pin", style="triangleup", location="belowbar", color="green")
plotshape(bear_pin, title="Bear Pin", style="triangledown", location="abovebar", color="red")
