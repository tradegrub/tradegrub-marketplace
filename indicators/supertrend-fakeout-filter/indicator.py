from tg_scripting import *
import numpy as np

indicator("Supertrend Fakeout Filter", overlay=True)

atr_len = input.int(10, "ATR Length", minval=1, maxval=50)
factor = input.float(3.0, "Factor", minval=0.5, maxval=10.0, step=0.5)
fakeout_bars = input.int(3, "Fakeout Check Bars", minval=1, maxval=10)
fakeout_atr_mult = input.float(0.5, "Min ATR Distance", minval=0.1, maxval=3.0, step=0.1)

cl = np.array(close, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

atr = np.array(ta.atr(high, low, close, atr_len), dtype=np.float64)

upper_band = np.zeros(n)
lower_band = np.zeros(n)
st = np.zeros(n)
direction = np.ones(n)

hl2 = (hi + lo) / 2.0

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

raw_flip = np.zeros(n, dtype=bool)
for i in range(1, n):
    if direction[i] != direction[i - 1]:
        raw_flip[i] = True

confirmed_bull = np.zeros(n, dtype=bool)
confirmed_bear = np.zeros(n, dtype=bool)
fakeout_signal = np.zeros(n, dtype=bool)

for i in range(1, n):
    if not raw_flip[i]:
        continue

    if np.isnan(atr[i]):
        continue

    min_dist = fakeout_atr_mult * atr[i]
    is_fakeout = False

    end = min(i + fakeout_bars + 1, n)
    if direction[i] == -1:
        for j in range(i, end):
            if cl[j] - st[i] < min_dist:
                is_fakeout = True
                break
    else:
        for j in range(i, end):
            if st[i] - cl[j] < min_dist:
                is_fakeout = True
                break

    if is_fakeout:
        fakeout_signal[i] = True
    elif direction[i] == -1:
        confirmed_bull[i] = True
    else:
        confirmed_bear[i] = True

st_colors = []
for i in range(n):
    st_colors.append("#26a69a" if direction[i] == -1 else "#ef5350")

plot(st.tolist(), title="Supertrend", color=st_colors, linewidth=2)

plotshape(confirmed_bull.tolist(), title="Confirmed Bull", style="triangleup",
          location="belowbar", color="#00e676", size="small")
plotshape(confirmed_bear.tolist(), title="Confirmed Bear", style="triangledown",
          location="abovebar", color="#ff1744", size="small")
plotshape(fakeout_signal.tolist(), title="Fakeout", style="xcross",
          location="abovebar", color="#ff9800", size="small")
