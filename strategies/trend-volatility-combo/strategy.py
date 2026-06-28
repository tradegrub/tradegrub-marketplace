from tg_scripting import *

# Inputs
st_len = input.int(10, "Supertrend Length", minval=5, maxval=50)
st_mult = input.float(3.0, "Supertrend Multiplier", minval=1.0, maxval=6.0)
atr_len = input.int(14, "ATR Length", minval=2, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
vol_avg_len = input.int(20, "Volume Average Length", minval=5, maxval=50)
vol_thresh = input.float(1.2, "Volume Threshold", minval=1.0, maxval=5.0)

# Calculations
supertrend = ta.supertrend(high, low, close, st_len, st_mult)
atr = ta.atr(high, low, close, atr_len)
vol_avg = ta.sma(volume, vol_avg_len)

# Supertrend direction: price above supertrend = bullish
st_bullish = close > supertrend
st_bearish = close < supertrend

# Volume filter
vol_confirmed = volume > (vol_avg * vol_thresh)

# Detect supertrend flips
prev_bullish = np.roll(st_bullish, 1)
prev_bullish[0] = False
prev_bearish = np.roll(st_bearish, 1)
prev_bearish[0] = False

st_flip_bull = st_bullish & prev_bearish
st_flip_bear = st_bearish & prev_bullish

# Entry on supertrend flip with volume confirmation
long_cond = st_flip_bull & vol_confirmed
short_cond = st_flip_bear & vol_confirmed

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long SL", from_entry="Long", stop=close[i] - atr[i] * atr_mult)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short SL", from_entry="Short", stop=close[i] + atr[i] * atr_mult)

# Plots
plot(supertrend, title="Supertrend", color="blue")
plot(atr, title="ATR", color="orange")
bgcolor(vol_confirmed, color="rgba(0, 200, 0, 0.05)")
bgcolor(st_bullish, color="rgba(0, 255, 0, 0.05)")
bgcolor(st_bearish, color="rgba(255, 0, 0, 0.05)")
