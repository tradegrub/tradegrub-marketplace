from tg_scripting import *
import numpy as np

length = input.int(50, "Length", minval=5, maxval=200)
alpha_val = input.float(0.5, "Alpha", minval=0.0, maxval=1.0)

src_close = np.array(close, dtype=float)
src_open = np.array(open, dtype=float)
n = len(src_close)

# Up and down differences
up_diff = np.maximum(src_close - src_open, 0.0)
down_diff = np.maximum(src_open - src_close, 0.0)

# EMA smoothing
ema_up = np.array(ta.ema(up_diff.tolist(), length), dtype=float)
ema_down = np.array(ta.ema(down_diff.tolist(), length), dtype=float)

# Bull and bear components with alpha cross-suppression
bull = ema_up - alpha_val * ema_down
bear = ema_down - alpha_val * ema_up

# Signal line
signal = bull - bear

plot(bull, title="Bull", color=color.green)
plot(bear, title="Bear", color=color.red)
plot(signal, title="Signal", color=color.blue)
hline(0, title="Zero", color=color.gray)
bgcolor(signal > 0, color="rgba(0,255,0,0.05)")
bgcolor(signal < 0, color="rgba(255,0,0,0.05)")
