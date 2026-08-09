# Rolling Beta — how much market risk this name is actually carrying.
from tg_scripting import *
import numpy as np

indicator("Rolling Beta", overlay=False)

benchmark = input.string("SPY", "Benchmark symbol")
window = input.int(60, "Regression window", minval=10, maxval=500)

c = np.asarray(close, dtype=float)
n = len(c)

bench = np.asarray(request.security(benchmark, timeframe.period, "close"), dtype=float)
if bench.shape[0] != n:
    bench = np.full(n, np.nan)

def returns(series):
    out = np.full(len(series), np.nan)
    prev = series[:-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        out[1:] = np.where(prev != 0, (series[1:] - prev) / prev, np.nan)
    return out

r_sym = returns(c)
r_ben = returns(bench)

beta = np.full(n, np.nan)
corr = np.full(n, np.nan)

for i in range(window, n):
    a = r_sym[i - window + 1:i + 1]
    b = r_ben[i - window + 1:i + 1]
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < max(5, window // 2):
        continue
    a, b = a[mask], b[mask]
    var_b = float(np.var(b))
    if var_b <= 0:
        continue
    # Beta is covariance over benchmark variance: the slope of the symbol's
    # returns regressed on the market's.
    beta[i] = float(np.cov(a, b, bias=True)[0, 1]) / var_b
    sd_a, sd_b = float(np.std(a)), float(np.std(b))
    if sd_a > 0 and sd_b > 0:
        corr[i] = float(np.mean((a - a.mean()) * (b - b.mean()))) / (sd_a * sd_b)

plot(beta, title="Beta", color="blue")
plot(corr, title="Correlation", color="gray")
hline(1.0, title="Market beta", color="orange")
hline(0.0, title="Zero", color="gray")
