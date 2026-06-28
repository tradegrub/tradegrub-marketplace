from tg_scripting import *

# Inputs
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=10, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=30)
bb_len = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0)

# Calculations
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, macd_sig)
bb_upper, bb_basis, bb_lower = ta.bb(close, bb_len, bb_mult)

# MACD crossover at BB extremes
macd_bull = ta.crossover(macd_line, signal_line)
macd_bear = ta.crossunder(macd_line, signal_line)

# Long: MACD bullish crossover when price is near or below lower band
long_cond = macd_bull & (close <= bb_basis)
# Short: MACD bearish crossover when price is near or above upper band
short_cond = macd_bear & (close >= bb_basis)

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
p_upper = plot(bb_upper, title="BB Upper", color="red")
p_lower = plot(bb_lower, title="BB Lower", color="green")
plot(bb_basis, title="BB Middle", color="gray")
fill(p_upper, p_lower, color="rgba(150, 150, 255, 0.1)")
plot(macd_line, title="MACD Line", color="blue")
plot(signal_line, title="Signal Line", color="orange")
