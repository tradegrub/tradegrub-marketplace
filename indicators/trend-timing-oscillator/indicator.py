from tg_scripting import *
import numpy as np

indicator("Trend Timing Oscillator", overlay=False)

length = input.int(25, "Aroon Length", minval=10, maxval=100)
maturity_len = input.int(10, "Maturity Window", minval=3, maxval=30)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(hi)

aroon_up = np.zeros(n)
aroon_down = np.zeros(n)
for i in range(length, n):
    hh_idx = np.argmax(hi[i-length:i+1])
    ll_idx = np.argmin(lo[i-length:i+1])
    aroon_up[i] = (hh_idx / length) * 100
    aroon_down[i] = (ll_idx / length) * 100

oscillator = aroon_up - aroon_down

maturity = np.zeros(n)
for i in range(maturity_len, n):
    window = oscillator[i-maturity_len:i+1]
    if oscillator[i] > 0:
        maturity[i] = np.sum(window > 0) / maturity_len * 100
    else:
        maturity[i] = -np.sum(window < 0) / maturity_len * 100

strong_up = (oscillator > 50) & (maturity > 70)
strong_down = (oscillator < -50) & (maturity < -70)

plot(oscillator.tolist(), title="Aroon Oscillator", color="#42a5f5", linewidth=2)
plot(maturity.tolist(), title="Trend Maturity", color="#ff9800", linewidth=1)
hline(50, title="Strong Up", color="#4CAF50", linestyle="dashed")
hline(-50, title="Strong Down", color="#f44336", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(strong_up.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(strong_down.tolist(), color="rgba(244,67,54,0.08)")
