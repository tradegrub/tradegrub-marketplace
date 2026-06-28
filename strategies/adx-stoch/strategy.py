from tg_scripting import *

# Inputs
adx_dilen = input.int(14, "DI Length", minval=2, maxval=50)
adx_adxlen = input.int(14, "ADX Length", minval=2, maxval=50)
adx_thresh = input.int(20, "ADX Threshold", minval=10, maxval=50)
stoch_len = input.int(14, "Stochastic Length", minval=2, maxval=50)
stoch_smooth = input.int(3, "Stochastic Smoothing", minval=1, maxval=10)
stoch_ob = input.int(80, "Stochastic Overbought", minval=60, maxval=95)
stoch_os = input.int(20, "Stochastic Oversold", minval=5, maxval=40)

# Calculations
plus_di, minus_di, adx_val = ta.dmi(high, low, close, adx_dilen)
stoch_k = ta.stoch(high, low, close, stoch_len)
k_smooth = ta.sma(stoch_k, stoch_smooth)
d_line = ta.sma(k_smooth, stoch_smooth)

# ADX trending + DI direction + Stochastic entry
trending = adx_val > adx_thresh
bullish_trend = trending & (plus_di > minus_di)
bearish_trend = trending & (minus_di > plus_di)

stoch_cross_up = ta.crossover(k_smooth, d_line)
stoch_cross_down = ta.crossunder(k_smooth, d_line)

long_cond = bullish_trend & stoch_cross_up & (k_smooth < stoch_ob)
short_cond = bearish_trend & stoch_cross_down & (k_smooth > stoch_os)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(adx_val, title="ADX", color="blue")
hline(adx_thresh, title="ADX Threshold", color="gray")
plot(k_smooth, title="Stoch %K", color="green")
plot(d_line, title="Stoch %D", color="red")
hline(stoch_ob, title="Overbought", color="red")
hline(stoch_os, title="Oversold", color="green")
