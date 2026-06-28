# NR7 (Narrowest Range of 7) Breakout Strategy
from tg_scripting import *

nr_period = input.int(7, "NR Period", minval=4, maxval=14)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
atr_tp_mult = input.float(2.5, "ATR Take Profit Multiplier", minval=1.0, maxval=5.0)
atr_sl_mult = input.float(1.0, "ATR Stop Loss Multiplier", minval=0.5, maxval=3.0)
use_volume = input.bool(True, "Require Volume Surge on Breakout")
vol_mult = input.float(1.3, "Volume Surge Multiplier", minval=1.0, maxval=3.0)

# Current bar range
bar_range = high - low
atr = ta.atr(high, low, close, atr_length)

# NR detection: current bar has the narrowest range of the last N bars
min_range = ta.lowest(bar_range, nr_period)
is_nr = bar_range <= min_range

# Volume filter
avg_vol = ta.sma(volume, 20)
vol_surge = volume > avg_vol * vol_mult if use_volume else np.ones(len(close), dtype=bool)

# Trade the breakout of the NR bar on the following bar
nr_prev = np.roll(is_nr, 1)
prev_high = np.roll(high, 1)
prev_low = np.roll(low, 1)

long_signal = nr_prev & (close > prev_high) & vol_surge
short_signal = nr_prev & (close < prev_low) & vol_surge

if long_signal[-1]:
    strategy.entry("Long", strategy.LONG)

if short_signal[-1]:
    strategy.entry("Short", strategy.SHORT)

# ATR-based exits
strategy.exit("Long TP/SL", from_entry="Long",
              limit=close[-1] + atr[-1] * atr_tp_mult,
              stop=close[-1] - atr[-1] * atr_sl_mult)
strategy.exit("Short TP/SL", from_entry="Short",
              limit=close[-1] - atr[-1] * atr_tp_mult,
              stop=close[-1] + atr[-1] * atr_sl_mult)

plot(atr, title="ATR", color="purple")
bgcolor(is_nr, color="rgba(255, 193, 7, 0.15)")
plotshape(long_signal, title="Long Breakout", style="triangleup", location="belowbar", color="green")
plotshape(short_signal, title="Short Breakout", style="triangledown", location="abovebar", color="red")
