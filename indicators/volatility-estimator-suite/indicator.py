from tg_scripting import *
import numpy as np

indicator("Volatility Estimator Suite", overlay=False)

lookback = input.int(20, "Lookback", minval=5, maxval=100)

o = np.array(open, dtype=float)
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

ln2 = np.log(2.0)

# Rolling volatility estimators
parkinson = np.full(n, np.nan)
garman_klass = np.full(n, np.nan)
rogers_satchell = np.full(n, np.nan)
yang_zhang = np.full(n, np.nan)

log_hl = np.log(h / l)
log_co = np.log(c / o)
log_hc = np.log(h / c)
log_ho = np.log(h / o)
log_lc = np.log(l / c)
log_lo = np.log(l / o)

for i in range(lookback, n):
    s = slice(i - lookback, i)

    # Parkinson
    parkinson[i] = np.sqrt(np.sum(log_hl[s] ** 2) / (4.0 * lookback * ln2))

    # Garman-Klass
    garman_klass[i] = np.sqrt(np.sum(0.5 * log_hl[s] ** 2 - (2.0 * ln2 - 1.0) * log_co[s] ** 2) / lookback)

    # Rogers-Satchell
    rs_vals = log_hc[s] * log_ho[s] + log_lc[s] * log_lo[s]
    rogers_satchell[i] = np.sqrt(np.maximum(np.sum(rs_vals) / lookback, 0.0))

    # Yang-Zhang: overnight variance + open-close variance + Rogers-Satchell
    log_oc = np.log(o[i - lookback + 1:i + 1] / c[i - lookback:i])  # overnight returns
    overnight_var = np.var(log_oc, ddof=1) if len(log_oc) > 1 else 0.0
    open_close_var = np.var(log_co[s], ddof=1)
    rs_var = np.maximum(np.sum(rs_vals) / lookback, 0.0)
    k = 0.34 / (1.34 + (lookback + 1) / (lookback - 1))
    yang_zhang[i] = np.sqrt(overnight_var + k * open_close_var + (1 - k) * rs_var)

plot(parkinson.tolist(), title="Parkinson", color="#26c6da")
plot(garman_klass.tolist(), title="Garman-Klass", color="#ff9800")
plot(rogers_satchell.tolist(), title="Rogers-Satchell", color="#ab47bc")
plot(yang_zhang.tolist(), title="Yang-Zhang", color="#66bb6a")
hline(0, title="Zero", color="#555555")
