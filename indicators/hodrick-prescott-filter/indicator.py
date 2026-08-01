from tg_scripting import *
import numpy as np

indicator("Hodrick-Prescott Filter", overlay=True)

lamb = input.int(1600, "Lambda (Smoothness)", minval=1, maxval=100000)
show_cycle = input.bool(True, "Show Cycle Component")

try:
    from scipy.sparse import eye, spdiags
    from scipy.sparse.linalg import spsolve
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

src = np.array(close, dtype=float)
n = len(src)

if HAS_SCIPY and n > 4:
    # HP filter via sparse matrix solution
    I = eye(n, format='csc')
    D = spdiags([np.ones(n), -2 * np.ones(n), np.ones(n)], [0, 1, 2], n - 2, n, format='csc')
    trend_hp = spsolve(I + lamb * D.T @ D, src)
else:
    # Fallback: simple double-smoothed EMA
    k = max(int(np.sqrt(lamb) / 2), 5)
    trend_hp = np.array(ta.sma(src.tolist(), min(k, n - 1)), dtype=float)

cycle = src - trend_hp

plot(trend_hp.tolist(), title="HP Trend", color="#42A5F5", linewidth=2)

if show_cycle:
    plot(cycle.tolist(), title="Cycle", color="#FF7043", linewidth=1)
