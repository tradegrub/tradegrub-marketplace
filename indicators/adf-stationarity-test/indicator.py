from tg_scripting import *
import numpy as np

indicator("Mean Reversion Detector", overlay=False)

lookback = input.int(50, "Lookback", minval=20, maxval=200)

src = np.array(close, dtype=float)
n = len(src)

t_stat = np.zeros(n)

for i in range(lookback, n):
    window = src[i - lookback + 1:i + 1]
    wlen = len(window)

    # ADF test: regress delta_y on y_lag
    y = window[1:]
    y_lag = window[:-1]
    delta_y = y - y_lag

    # Add constant term: [y_lag, 1]
    X = np.column_stack([y_lag, np.ones(len(y_lag))])

    # Least squares
    result = np.linalg.lstsq(X, delta_y, rcond=None)
    coeffs = result[0]
    gamma = float(coeffs[0])

    # Compute residuals and standard error
    fitted = X @ coeffs
    residuals = delta_y - fitted
    s2 = float(np.sum(residuals ** 2) / max(1, len(residuals) - 2))

    # Standard error of gamma
    XtX_inv = np.linalg.inv(X.T @ X)
    se_gamma = np.sqrt(max(0.0, s2 * float(XtX_inv[0, 0])))

    if se_gamma > 0:
        t_stat[i] = gamma / se_gamma
    else:
        t_stat[i] = 0.0

plot(t_stat.tolist(), title="ADF t-Statistic", color="#42A5F5", linewidth=2)
hline(-2.86, title="5% Critical Value", color="#FFA726", linestyle="dashed")
hline(-3.43, title="1% Critical Value", color="#EF5350", linestyle="dashed")
hline(0, title="Zero", color="#666666", linestyle="dashed")

# Background when stationary at 5% level
is_stationary = t_stat < -2.86
bgcolor(is_stationary.tolist(), color="rgba(76,175,80,0.1)")
