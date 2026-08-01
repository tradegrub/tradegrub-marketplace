from tg_scripting import *
import numpy as np

indicator("Three Candle Sweep", overlay=True)

show_labels = input.bool(True, "Show Labels")
cooldown = input.int(3, "Cooldown Bars", minval=1, maxval=20)
show_bg = input.bool(True, "Highlight Signal Bars")

op = np.array(open, dtype=float)
cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

bull_signal = np.zeros(n, dtype=bool)
bear_signal = np.zeros(n, dtype=bool)

last_bull = -999
last_bear = -999

for i in range(2, n):
    # Bearish two-candle run (two green candles), then bullish sweep down
    if (op[i-2] < cl[i-2] and op[i-1] < cl[i-1]
            and cl[i] < op[i-2]
            and i - last_bear >= cooldown):
        bear_signal[i] = True
        last_bear = i

    # Bullish two-candle run (two red candles), then bearish sweep up
    if (op[i-2] > cl[i-2] and op[i-1] > cl[i-1]
            and cl[i] > op[i-2]
            and i - last_bull >= cooldown):
        bull_signal[i] = True
        last_bull = i

if show_labels:
    for i in range(n):
        if bull_signal[i]:
            label.new(x=i, y=float(lo[i]),
                      text="",
                      style=label.style_label_up,
                      color="#26a69a",
                      size="tiny")
        if bear_signal[i]:
            label.new(x=i, y=float(hi[i]),
                      text="",
                      style=label.style_label_down,
                      color="#ef5350",
                      size="tiny")

if show_bg:
    bull_bg = bull_signal.tolist()
    bear_bg = bear_signal.tolist()
    bgcolor(bull_bg, color="rgba(38,166,154,0.12)")
    bgcolor(bear_bg, color="rgba(239,83,80,0.12)")
