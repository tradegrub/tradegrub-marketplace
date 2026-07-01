from tg_scripting import *
import numpy as np

indicator("Cybernetic Oscillator", overlay=False)

hp_length = input.int(10, "Highpass Length", minval=2, maxval=50)
lp_length = input.int(20, "Lowpass Length", minval=5, maxval=100)

cl = np.array(close, dtype=float)
n = len(cl)

hp_ema = np.array(ta.ema(close, hp_length), dtype=float)
hp_ema = np.nan_to_num(hp_ema, nan=cl[0] if n > 0 else 0.0)
highpass = cl - hp_ema

lp_alpha = 2.0 / (lp_length + 1)
bandpass = np.zeros(n)
bandpass[0] = highpass[0]
for i in range(1, n):
    bandpass[i] = lp_alpha * highpass[i] + (1 - lp_alpha) * bandpass[i - 1]

bp_norm = np.zeros(n)
lookback = max(hp_length, lp_length) * 2
for i in range(lookback, n):
    window = bandpass[i - lookback:i + 1]
    mx = np.max(np.abs(window))
    if mx > 0:
        bp_norm[i] = bandpass[i] / mx * 100

trigger = np.zeros(n)
trigger[0] = bp_norm[0]
t_alpha = 2.0 / (max(hp_length // 2, 2) + 1)
for i in range(1, n):
    trigger[i] = t_alpha * bp_norm[i] + (1 - t_alpha) * trigger[i - 1]

cross_up = np.zeros(n, dtype=bool)
cross_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if bp_norm[i] > trigger[i] and bp_norm[i - 1] <= trigger[i - 1]:
        cross_up[i] = True
    elif bp_norm[i] < trigger[i] and bp_norm[i - 1] >= trigger[i - 1]:
        cross_down[i] = True

plot(bp_norm.tolist(), title="Bandpass", color="#26c6da", linewidth=2)
plot(trigger.tolist(), title="Trigger", color="#ff9800", linewidth=1)
hline(0, title="Zero", color="#555555", linestyle="dashed")
hline(60, title="Upper", color="#f44336", linestyle="dashed")
hline(-60, title="Lower", color="#4CAF50", linestyle="dashed")
bgcolor(cross_up.tolist(), color="rgba(0,230,118,0.1)")
bgcolor(cross_down.tolist(), color="rgba(255,23,68,0.1)")
plotshape(cross_up.tolist(), title="Bull Signal", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(cross_down.tolist(), title="Bear Signal", style="triangledown", location="abovebar", color="#ff1744", size="small")
