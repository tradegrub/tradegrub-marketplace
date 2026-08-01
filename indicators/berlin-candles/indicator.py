from tg_scripting import *
import numpy as np

indicator("Smoothed Price Candles", overlay=True)

smooth_length = input.int(5, "Smooth Length", minval=2, maxval=20)

o = np.array(open, dtype=float)
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

def ema(data, length):
    out = np.copy(data)
    alpha = 2.0 / (length + 1)
    for i in range(1, len(data)):
        out[i] = alpha * data[i] + (1 - alpha) * out[i - 1]
    return out

# Smoothed OHLC
smooth_open = ema(o, smooth_length)
smooth_high_ema = ema(h, smooth_length)
smooth_low_ema = ema(l, smooth_length)

# Preserve extremes: smoothed high >= actual high, smoothed low <= actual low
smooth_high = np.maximum(h, smooth_high_ema)
smooth_low = np.minimum(l, smooth_low_ema)

# Close is actual close (price-preserving)
smooth_close = c

plot(smooth_open.tolist(), title="Smoothed Open", color="#90caf9")
plot(smooth_high.tolist(), title="Smoothed High", color="#66bb6a")
plot(smooth_low.tolist(), title="Smoothed Low", color="#ef5350")
plot(smooth_close.tolist(), title="Close", color="#ffffff", linewidth=2)
