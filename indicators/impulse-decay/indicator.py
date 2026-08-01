from tg_scripting import *
import numpy as np

indicator("Impulse Decay Coefficient", overlay=False)

atr_mult = input.float(2.0, "ATR Multiplier", minval=1.0, maxval=5.0)
lookback = input.int(20, "Lookback", minval=5, maxval=100)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_vals = np.array(ta.atr(high, low, close, lookback), dtype=float)

# Detect impulse moves: bar range normalized by ATR
bar_move = np.abs(cl - np.roll(cl, 1))
bar_move[0] = 0.0

# Track impulse and decay
decay = np.zeros(n)
impulse_price = np.zeros(n)
impulse_size = np.zeros(n)
in_impulse = False
imp_start = 0.0
imp_sz = 0.0

for i in range(lookback, n):
    atr_val = float(atr_vals[i])
    if atr_val <= 0:
        continue
    move = float(bar_move[i])

    if not in_impulse and move > atr_val * float(atr_mult):
        in_impulse = True
        imp_start = float(cl[i])
        imp_sz = move

    if in_impulse:
        retracement = abs(float(cl[i]) - imp_start)
        decay_val = min((retracement / imp_sz) * 100.0, 150.0) if imp_sz > 0 else 0.0
        decay[i] = decay_val
        if decay_val >= 100.0:
            in_impulse = False
    else:
        decay[i] = 0.0

plot(decay.tolist(), title="Decay Coefficient", color="#FF7043")
hline(100, title="Full Absorption", color="#EF5350")
hline(50, title="Half Absorbed", color="#FFA726")
hline(0, title="Zero", color="#555555")
