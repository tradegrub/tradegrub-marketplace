from tg_scripting import *
import numpy as np

indicator("Negative Volume Index", overlay=False)

signal_len = input.int(255, "Signal Length", minval=10, maxval=500)
show_signal = input.bool(True, "Show Signal Line")

close_arr = np.array(close, dtype=float)
vol_arr = np.array(volume, dtype=float)
n = len(close_arr)

nvi = np.ones(n) * 1000.0

for i in range(1, n):
    if vol_arr[i] < vol_arr[i - 1]:
        pct = (close_arr[i] - close_arr[i - 1]) / close_arr[i - 1] if close_arr[i - 1] != 0 else 0.0
        nvi[i] = nvi[i - 1] * (1.0 + pct)
    else:
        nvi[i] = nvi[i - 1]

nvi_signal = ta.ema(nvi.tolist(), signal_len)

bull = np.array(nvi > np.array(nvi_signal, dtype=float))

plot(nvi.tolist(), title="NVI", color="#AB47BC", linewidth=2)
if show_signal:
    plot(nvi_signal, title="Signal", color="#FFA726", linewidth=1)
