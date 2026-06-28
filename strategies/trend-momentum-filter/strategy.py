from tg_scripting import *

# Inputs
adx_dilen = input.int(14, "DI Length", minval=2, maxval=50)
adx_adxlen = input.int(14, "ADX Length", minval=2, maxval=50)
adx_thresh = input.int(25, "ADX Trend Threshold", minval=10, maxval=50)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(65, "RSI Long Entry Above", minval=50, maxval=80)
rsi_os = input.int(35, "RSI Short Entry Below", minval=20, maxval=50)

# Calculations
plus_di, minus_di, adx_val = ta.dmi(high, low, close, adx_dilen)
rsi = ta.rsi(close, rsi_len)

# Conditions - ADX confirms trend, DI gives direction, RSI gives momentum
trending = adx_val > adx_thresh
long_cond = trending & (plus_di > minus_di) & (rsi > rsi_ob)
short_cond = trending & (minus_di > plus_di) & (rsi < rsi_os)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(adx_val, title="ADX", color="blue")
plot(plus_di, title="+DI", color="green")
plot(minus_di, title="-DI", color="red")
hline(adx_thresh, title="Trend Threshold", color="gray")
