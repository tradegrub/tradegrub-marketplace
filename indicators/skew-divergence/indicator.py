from tg_scripting import *
import numpy as np

indicator("Skew Divergence Oscillator", overlay=False)

lookback = input.int(30, "Lookback", minval=10, maxval=100)

cl = np.array(close, dtype=float)
n = len(cl)

# Compute log returns
returns = np.zeros(n)
returns[1:] = np.log(cl[1:] / cl[:-1])

# Rolling skewness: E[(x-mu)^3] / sigma^3
skewness = np.zeros(n)
for i in range(lookback, n):
    window = returns[i - lookback:i]
    mu = np.mean(window)
    sigma = np.std(window)
    if sigma > 1e-10:
        skewness[i] = np.mean(((window - mu) / sigma) ** 3)

# Detect divergence: price makes new high but skewness is negative
rolling_high = np.zeros(n)
for i in range(lookback, n):
    rolling_high[i] = np.max(cl[i - lookback:i + 1])

new_high = (cl >= rolling_high) & (np.arange(n) >= lookback)
bearish_div = (new_high) & (skewness < 0)

# Bullish divergence: price makes new low but skewness is positive
rolling_low = np.full(n, np.inf)
for i in range(lookback, n):
    rolling_low[i] = np.min(cl[i - lookback:i + 1])

new_low = (cl <= rolling_low) & (np.arange(n) >= lookback)
bullish_div = (new_low) & (skewness > 0)

plot(skewness.tolist(), title="Skewness", color="#42A5F5")
hline(0, title="Zero", color="#555555")
plotshape(bearish_div.tolist(), title="Bearish Divergence", style="triangledown",
          location="abovebar", color="#EF5350")
plotshape(bullish_div.tolist(), title="Bullish Divergence", style="triangleup",
          location="belowbar", color="#26A69A")
