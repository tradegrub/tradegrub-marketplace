# Inside Bar Breakout Strategy
from tg_scripting import *

atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_tp_mult = input.float(2.0, "ATR Take Profit Multiplier", minval=1.0, maxval=5.0)
atr_sl_mult = input.float(0.5, "ATR Stop Buffer", minval=0.1, maxval=2.0)
require_trend = input.bool(True, "Require Trend Alignment")
ma_length = input.int(50, "Trend MA Length", minval=10, maxval=200)

atr = ta.atr(high, low, close, atr_length)
trend_ma = ta.sma(close, ma_length)

# Detect inside bars: current bar's range is entirely within prior bar's range
prev_high = np.roll(high, 1)
prev_low = np.roll(low, 1)
inside_bar = (high <= prev_high) & (low >= prev_low)

# Breakout of mother bar (previous bar) range
long_signal = ta.crossover(close, prev_high) & np.roll(inside_bar, 1)
short_signal = ta.crossunder(close, prev_low) & np.roll(inside_bar, 1)

# Optional trend filter
if require_trend:
    long_signal = long_signal & (close > trend_ma)
    short_signal = short_signal & (close < trend_ma)

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# TP and SL based on ATR
strategy.exit("Long TP/SL", from_entry="Long",
              limit=close[-1] + atr[-1] * atr_tp_mult,
              stop=prev_low[-1] - atr[-1] * atr_sl_mult)
strategy.exit("Short TP/SL", from_entry="Short",
              limit=close[-1] - atr[-1] * atr_tp_mult,
              stop=prev_high[-1] + atr[-1] * atr_sl_mult)

plot(trend_ma, title="Trend MA", color="blue")
bgcolor(inside_bar, color="rgba(156, 39, 176, 0.1)")
plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")
