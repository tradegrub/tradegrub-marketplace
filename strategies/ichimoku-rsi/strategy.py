from tg_scripting import *

# Inputs
tenkan_len = input.int(9, "Tenkan-sen Period", minval=2, maxval=50)
kijun_len = input.int(26, "Kijun-sen Period", minval=5, maxval=100)
senkou_b_len = input.int(52, "Senkou Span B Period", minval=10, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(70, "RSI Overbought", minval=50, maxval=90)
rsi_os = input.int(30, "RSI Oversold", minval=10, maxval=50)

# Calculations
tenkan, kijun, senkou_a, senkou_b, chikou = ta.ichimoku(high, low, close, tenkan_len, kijun_len, senkou_b_len)
rsi = ta.rsi(close, rsi_len)

# Cloud bullish: price above both senkou spans, tenkan above kijun
cloud_top = np.maximum(senkou_a, senkou_b)
cloud_bot = np.minimum(senkou_a, senkou_b)

long_cond = (close > cloud_top) & (tenkan > kijun) & (rsi > 50) & (rsi < rsi_ob)
short_cond = (close < cloud_bot) & (tenkan < kijun) & (rsi < 50) & (rsi > rsi_os)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(tenkan, title="Tenkan-sen", color="blue")
plot(kijun, title="Kijun-sen", color="red")
p_a = plot(senkou_a, title="Senkou A", color="green")
p_b = plot(senkou_b, title="Senkou B", color="maroon")
fill(p_a, p_b, color="rgba(0, 255, 0, 0.1)")
