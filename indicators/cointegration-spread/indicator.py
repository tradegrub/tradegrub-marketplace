from tg_scripting import *
import numpy as np

indicator("Spread Analyzer", overlay=False)

lookback = input.int(100, "Lookback", minval=30, maxval=500)

src = np.array(close, dtype=float)
n = len(src)

spread = np.full(n, np.nan)
zscore = np.full(n, np.nan)
upper_band = np.full(n, np.nan)
lower_band = np.full(n, np.nan)
var_ratio_line = np.full(n, np.nan)

for i in range(lookback, n):
    window = src[i - lookback:i + 1]
    x = np.arange(len(window), dtype=float)

    # Linear regression using numpy lstsq
    A = np.column_stack([x, np.ones(len(x))])
    result = np.linalg.lstsq(A, window, rcond=None)
    coeffs = result[0]
    fitted = A @ coeffs

    # Residual spread
    residuals = window - fitted
    spread[i] = residuals[-1]

    mu = np.mean(residuals)
    sigma = np.std(residuals)
    if sigma > 0:
        zscore[i] = (residuals[-1] - mu) / sigma
        upper_band[i] = 2.0
        lower_band[i] = -2.0

    # Variance ratio test for stationarity
    k = min(10, lookback // 4)
    if len(residuals) > k:
        var_1 = np.var(np.diff(residuals))
        diffs_k = residuals[k:] - residuals[:-k]
        var_k = np.var(diffs_k) / k if len(diffs_k) > 0 else var_1
        var_ratio_line[i] = var_k / var_1 if var_1 > 0 else 1.0

# Mean reversion signals
mr_buy = (zscore < -2.0) & ~np.isnan(zscore)
mr_sell = (zscore > 2.0) & ~np.isnan(zscore)

plot(zscore.tolist(), title="Z-Score", color="#00e5ff")
plot(upper_band.tolist(), title="+2 Std", color="#f44336")
plot(lower_band.tolist(), title="-2 Std", color="#4CAF50")
hline(0, title="Zero", color="#888888")
plotshape(mr_buy.tolist(), title="Mean Rev Buy", style="triangleup", location="bottom", color="#4CAF50")
plotshape(mr_sell.tolist(), title="Mean Rev Sell", style="triangledown", location="top", color="#f44336")
