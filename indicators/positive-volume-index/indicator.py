from tg_scripting import *
import numpy as np

indicator("Positive Volume Index", overlay=False)

signal_len = input.int(255, "Signal Length", minval=10, maxval=500)
show_signal = input.bool(True, "Show Signal Line")

close_arr = np.array(close, dtype=float)
vol_arr = np.array(volume, dtype=float)
n = len(close_arr)

pvi = np.ones(n) * 1000.0

for i in range(1, n):
    if vol_arr[i] > vol_arr[i - 1]:
        pct = (close_arr[i] - close_arr[i - 1]) / close_arr[i - 1] if close_arr[i - 1] != 0 else 0.0
        pvi[i] = pvi[i - 1] * (1.0 + pct)
    else:
        pvi[i] = pvi[i - 1]

pvi_signal = ta.ema(pvi.tolist(), signal_len)

bull = np.array(pvi > np.array(pvi_signal, dtype=float))

plot(pvi.tolist(), title="PVI", color="#42A5F5", linewidth=2)
if show_signal:
    plot(pvi_signal, title="Signal", color="#FFA726", linewidth=1)
