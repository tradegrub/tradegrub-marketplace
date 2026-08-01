from tg_scripting import *
import numpy as np

indicator("Zero Lag EMA", overlay=True)

length = input.int(21, "Length", minval=2, maxval=200)
show_ema = input.bool(True, "Show Standard EMA")

src = np.array(close)
n = len(src)

# Standard EMA for reference
ema_line = np.array(ta.ema(close, length))

# Zero Lag EMA: EMA of (2*src - EMA(src))
lag = (length - 1) // 2
ema1 = np.array(ta.ema(close, length))
# Error correction: src + (src - ema_lagged)
corrected = (2.0 * src - ema1).tolist()
zlema = np.array(ta.ema(corrected, length))

# Cross signals
cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if zlema[i] > ema_line[i] and zlema[i - 1] <= ema_line[i - 1]:
        cross_up[i] = True
    elif zlema[i] < ema_line[i] and zlema[i - 1] >= ema_line[i - 1]:
        cross_down[i] = True

plot(zlema.tolist(), title="ZLEMA", color="#00e676", linewidth=2)
if show_ema:
    plot(ema_line.tolist(), title="EMA", color="rgba(255,255,255,0.3)", linewidth=1)
plotshape(cross_up, title="Cross Up", style="triangleup", location="belowbar", color="#00e676")
plotshape(cross_down, title="Cross Down", style="triangledown", location="abovebar", color="#ff1744")
