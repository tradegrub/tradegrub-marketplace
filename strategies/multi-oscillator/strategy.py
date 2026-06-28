from tg_scripting import *

# Inputs
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
cci_len = input.int(20, "CCI Length", minval=5, maxval=50)
stoch_len = input.int(14, "Stochastic Length", minval=2, maxval=50)
stoch_smooth = input.int(3, "Stochastic Smoothing", minval=1, maxval=10)
consensus = input.int(2, "Min Consensus (2 or 3)", minval=2, maxval=3)

# Calculations
rsi = ta.rsi(close, rsi_len)
cci = ta.cci(close, cci_len)
stoch_k = ta.stoch(high, low, close, stoch_len)
k_smooth = ta.sma(stoch_k, stoch_smooth)

# Individual signals
rsi_bull = rsi > 50
rsi_bear = rsi < 50
cci_bull = cci > 0
cci_bear = cci < 0
stoch_bull = k_smooth > 50
stoch_bear = k_smooth < 50

# Consensus scoring
bull_score = rsi_bull.astype(int) + cci_bull.astype(int) + stoch_bull.astype(int)
bear_score = rsi_bear.astype(int) + cci_bear.astype(int) + stoch_bear.astype(int)

long_cond = bull_score >= consensus
short_cond = bear_score >= consensus

# Track previous state to only enter on new consensus
prev_long = np.roll(long_cond, 1)
prev_long[0] = False
prev_short = np.roll(short_cond, 1)
prev_short[0] = False

new_long = long_cond & ~prev_long
new_short = short_cond & ~prev_short

for i in range(len(close)):
    if new_long[i]:
        strategy.entry("Long", strategy.LONG)
    elif new_short[i]:
        strategy.entry("Short", strategy.SHORT)

# Plots
plot(rsi, title="RSI", color="blue")
plot(cci / 4 + 50, title="CCI (scaled)", color="orange")
plot(k_smooth, title="Stochastic %K", color="purple")
hline(50, title="Midline", color="gray")
