from tg_scripting import *
import numpy as np

indicator("Tail Risk Oscillator", overlay=False)

lookback = input.int(50, "Lookback", minval=20, maxval=200)

cl = np.array(close, dtype=float)
n = len(cl)

# Compute log returns
returns = np.zeros(n)
returns[1:] = np.log(cl[1:] / cl[:-1])

# Rolling kurtosis and skewness
kurtosis = np.zeros(n)
skewness = np.zeros(n)

for i in range(lookback, n):
    window = returns[i - lookback:i]
    mu = np.mean(window)
    sigma = np.std(window)
    if sigma > 1e-10:
        standardized = (window - mu) / sigma
        kurtosis[i] = np.mean(standardized ** 4) - 3.0  # excess kurtosis
        skewness[i] = np.mean(standardized ** 3)

# High tail risk zones
high_risk = (kurtosis > 3.0).tolist()

plot(kurtosis.tolist(), title="Excess Kurtosis", color="#FF7043")
plot(skewness.tolist(), title="Skewness", color="#42A5F5")
hline(3, title="High Tail Risk", color="#EF5350")
hline(0, title="Zero", color="#555555")
bgcolor(high_risk, color="rgba(239,83,80,0.08)")
