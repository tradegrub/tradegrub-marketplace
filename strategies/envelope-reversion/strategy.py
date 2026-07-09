from tg_scripting import *
import numpy as np

indicator("Moving Average Envelope Reversion", overlay=True)

ma_len = input.int(20, "MA Length", minval=5, maxval=200)
env_pct = input.float(2.0, "Envelope %", minval=0.5, maxval=10.0, step=0.1)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
sl_mult = input.float(1.5, "Stop Loss ATR Mult", minval=0.5, maxval=5.0, step=0.1)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

ma = ta.sma(close, ma_len)
ma_arr = np.array(ma, dtype=float)
atr = np.array(ta.atr(high, low, close, atr_len), dtype=float)

upper_env = ma_arr * (1.0 + env_pct / 100.0)
lower_env = ma_arr * (1.0 - env_pct / 100.0)

long_entry = np.zeros(n, dtype=bool)
short_entry = np.zeros(n, dtype=bool)
in_long = False
in_short = False

for i in range(1, n):
    strategy.set_bar_index(i)
    if not in_long and src[i] <= lower_env[i] and src[i - 1] > lower_env[i - 1]:
        long_entry[i] = True
        in_long = True
        in_short = False
        sl = src[i] - atr[i] * sl_mult
        tp = ma_arr[i]
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long", stop=sl, limit=tp)
    elif not in_short and src[i] >= upper_env[i] and src[i - 1] < upper_env[i - 1]:
        short_entry[i] = True
        in_short = True
        in_long = False
        sl = src[i] + atr[i] * sl_mult
        tp = ma_arr[i]
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short", stop=sl, limit=tp)
    elif in_long and src[i] >= ma_arr[i]:
        in_long = False
        strategy.close("Long")
    elif in_short and src[i] <= ma_arr[i]:
        in_short = False
        strategy.close("Short")

plot(ma, title="MA", color="#FFD54F", linewidth=2)
plot(upper_env.tolist(), title="Upper Envelope", color="#EF5350", linewidth=1)
plot(lower_env.tolist(), title="Lower Envelope", color="#66BB6A", linewidth=1)
plotshape(long_entry, title="Long", style="triangleup", location="belowbar", color="#66BB6A")
plotshape(short_entry, title="Short", style="triangledown", location="abovebar", color="#EF5350")
