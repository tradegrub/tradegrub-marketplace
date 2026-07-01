from tg_scripting import *
import numpy as np

length = input.int(20, "Length", minval=5, maxval=100)

c = np.array(close, dtype=float)
n = len(c)

mono_score = np.full(n, 50.0)
direction = np.zeros(n)

for i in range(length, n):
    seg = c[i - length:i]
    pairs = np.diff(seg)
    inc = np.sum(pairs >= 0)
    dec = np.sum(pairs < 0)
    total = len(pairs)
    mono_score[i] = max(inc, dec) / total * 100.0
    direction[i] = 1.0 if inc >= dec else -1.0

plot(mono_score, title="Monotonicity Index", color="#00e5ff")
hline(80, title="Strong Trend", color="#666666")
hline(50, title="Random", color="#444444")
bgcolor(mono_score > 80, color="rgba(0, 255, 200, 0.08)")
