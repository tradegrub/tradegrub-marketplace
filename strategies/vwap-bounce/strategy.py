# VWAP Bounce/Rejection Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
bounce_mult = input.float(0.5, "Bounce ATR Multiplier", minval=0.1, maxval=2.0)
exit_mult = input.float(1.5, "Exit ATR Multiplier", minval=0.5, maxval=5.0)
trend_len = input.int(50, "Trend SMA Length", minval=10, maxval=200)

vwap_val = ta.vwap(high, low, close, volume)
atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, trend_len)

# Price near VWAP (within bounce_mult * ATR)
near_vwap = np.abs(close - vwap_val) < bounce_mult * atr

# Bullish bounce: price near VWAP in uptrend
bull_bounce = near_vwap & (close > trend_sma) & (close > vwap_val)
# Bearish rejection: price near VWAP in downtrend
bear_reject = near_vwap & (close < trend_sma) & (close < vwap_val)

if bull_bounce[-1]:
    strategy.entry("Long", strategy.LONG)
if bear_reject[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when price moves away from VWAP by exit_mult * ATR
long_exit = close[-1] > vwap_val[-1] + exit_mult * atr[-1]
short_exit = close[-1] < vwap_val[-1] - exit_mult * atr[-1]

if long_exit:
    strategy.close("Long")
if short_exit:
    strategy.close("Short")

plot(vwap_val, title="VWAP", color="blue")
plot(trend_sma, title="Trend SMA", color="orange")
bgcolor(bull_bounce[-1], color="rgba(0,255,0,0.1)")
bgcolor(bear_reject[-1], color="rgba(255,0,0,0.1)")
