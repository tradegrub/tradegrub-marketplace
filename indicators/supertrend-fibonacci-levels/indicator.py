from tg_scripting import *
import numpy as np

indicator("Supertrend Fibonacci Levels", overlay=True)

atr_len = input.int(10, "ATR Length", minval=1, maxval=50)
factor = input.float(3.0, "Factor", minval=0.5, maxval=10.0, step=0.5)
show_fib = input.bool(True, "Show Fibonacci Levels")

cl = np.array(close, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

atr = np.array(ta.atr(high, low, close, atr_len), dtype=np.float64)

hl2 = (hi + lo) / 2.0
upper_band = np.zeros(n)
lower_band = np.zeros(n)
st = np.zeros(n)
direction = np.ones(n)

for i in range(1, n):
    if np.isnan(atr[i]):
        st[i] = cl[i]
        continue

    ub = hl2[i] + factor * atr[i]
    lb = hl2[i] - factor * atr[i]

    upper_band[i] = ub if ub < upper_band[i - 1] or cl[i - 1] > upper_band[i - 1] else upper_band[i - 1]
    lower_band[i] = lb if lb > lower_band[i - 1] or cl[i - 1] < lower_band[i - 1] else lower_band[i - 1]

    if st[i - 1] == upper_band[i - 1]:
        direction[i] = -1 if cl[i] > upper_band[i] else 1
    else:
        direction[i] = 1 if cl[i] < lower_band[i] else -1

    st[i] = lower_band[i] if direction[i] == -1 else upper_band[i]

fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
fib_colors = ["rgba(255,235,59,0.3)", "rgba(255,152,0,0.3)", "rgba(33,150,243,0.4)",
              "rgba(255,152,0,0.3)", "rgba(255,235,59,0.3)"]

swing_hi = np.nan
swing_lo = np.nan
last_dir = 1

fib_lines = [np.full(n, np.nan) for _ in fib_levels]

for i in range(1, n):
    if direction[i] != last_dir:
        if direction[i] == -1:
            swing_lo = float(st[i])
            swing_hi = float(np.max(hi[max(0, i - 20):i + 1]))
        else:
            swing_hi = float(st[i])
            swing_lo = float(np.min(lo[max(0, i - 20):i + 1]))
        last_dir = direction[i]

    if not np.isnan(swing_hi) and not np.isnan(swing_lo) and show_fib:
        rng = swing_hi - swing_lo
        if direction[i] == -1:
            for f_idx, fib in enumerate(fib_levels):
                fib_lines[f_idx][i] = swing_hi - rng * fib
        else:
            for f_idx, fib in enumerate(fib_levels):
                fib_lines[f_idx][i] = swing_lo + rng * fib

st_colors = ["#26a69a" if direction[i] == -1 else "#ef5350" for i in range(n)]
plot(st.tolist(), title="Supertrend", color=st_colors, linewidth=2)

for f_idx, fib in enumerate(fib_levels):
    plot(fib_lines[f_idx].tolist(), title=f"Fib {fib}", color=fib_colors[f_idx], linewidth=1)
