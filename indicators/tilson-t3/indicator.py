from tg_scripting import *
import numpy as np

length = input.int(20, "Length", minval=1, maxval=200)
volume_factor = input.float(0.7, "Volume Factor", minval=0.0, maxval=1.0)

src = np.array(close, dtype=float)
n = len(src)
a = volume_factor

# T3 coefficients
c1 = -(a ** 3)
c2 = 3.0 * a ** 2 + 3.0 * a ** 3
c3 = -6.0 * a ** 2 - 3.0 * a - 3.0 * a ** 3
c4 = 1.0 + 3.0 * a + a ** 3 + 3.0 * a ** 2

# Iterative EMA computation
def ema_calc(data, period):
    result = np.empty(n, dtype=float)
    alpha = 2.0 / (period + 1)
    result[0] = data[0]
    for i in range(1, n):
        result[i] = alpha * data[i] + (1.0 - alpha) * result[i - 1]
    return result

e1 = ema_calc(src, length)
e2 = ema_calc(e1, length)
e3 = ema_calc(e2, length)
e4 = ema_calc(e3, length)
e5 = ema_calc(e4, length)
e6 = ema_calc(e5, length)

t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

# Signal line
signal_len = 5
signal = np.empty(n, dtype=float)
signal[:signal_len - 1] = t3[:signal_len - 1]
for i in range(signal_len - 1, n):
    signal[i] = np.mean(t3[i - signal_len + 1:i + 1])

# Direction coloring
t3_rising = np.zeros(n, dtype=bool)
t3_rising[1:] = t3[1:] > t3[:-1]

plot(t3, title="Tilson T3", color="#2196f3")
plot(signal, title="Signal", color="#ff9800")
