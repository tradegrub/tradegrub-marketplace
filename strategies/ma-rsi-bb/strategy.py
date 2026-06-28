from tg_scripting import *

# Inputs
ma_len = input.int(50, "Moving Average Length", minval=5, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(70, "RSI Overbought", minval=50, maxval=90)
rsi_os = input.int(30, "RSI Oversold", minval=10, maxval=50)
bb_len = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0)

# Calculations
ma = ta.sma(close, ma_len)
rsi = ta.rsi(close, rsi_len)
bb_upper, bb_basis, bb_lower = ta.bb(close, bb_len, bb_mult)

# Long: price above MA (uptrend), RSI not overbought, price touches lower BB (pullback)
long_cond = (close > ma) & (rsi < rsi_ob) & (close <= bb_lower)
# Short: price below MA (downtrend), RSI not oversold, price touches upper BB (pullback)
short_cond = (close < ma) & (rsi > rsi_os) & (close >= bb_upper)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
p_upper = plot(bb_upper, title="BB Upper", color="red")
p_lower = plot(bb_lower, title="BB Lower", color="green")
plot(bb_basis, title="BB Basis", color="gray")
plot(ma, title="SMA", color="blue")
fill(p_upper, p_lower, color="rgba(100, 100, 255, 0.1)")
