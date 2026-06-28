from tg_scripting import *

# Inputs - Elder Triple Screen
ema_len = input.int(13, "Trend EMA Length", minval=5, maxval=100)
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=30)
stoch_len = input.int(14, "Stochastic Length", minval=2, maxval=50)
stoch_ob = input.int(80, "Stochastic Overbought", minval=60, maxval=95)
stoch_os = input.int(20, "Stochastic Oversold", minval=5, maxval=40)

# Screen 1: Trend (EMA slope)
ema_trend = ta.ema(close, ema_len)
ema_slope = ta.change(ema_trend, 1)
uptrend = ema_slope > 0
downtrend = ema_slope < 0

# Screen 2: Momentum (MACD histogram)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_sig)
hist_rising = ta.change(hist, 1) > 0
hist_falling = ta.change(hist, 1) < 0

# Screen 3: Entry (Stochastic)
stoch_k = ta.stoch(high, low, close, stoch_len)
stoch_smooth = ta.sma(stoch_k, 3)

# Triple screen logic
long_cond = uptrend & hist_rising & (stoch_smooth < stoch_os)
short_cond = downtrend & hist_falling & (stoch_smooth > stoch_ob)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(ema_trend, title="Trend EMA", color="blue")
plot(hist, title="MACD Histogram", color="teal")
plot(stoch_smooth, title="Stochastic %K", color="purple")
hline(stoch_ob, title="Stoch OB", color="red")
hline(stoch_os, title="Stoch OS", color="green")
