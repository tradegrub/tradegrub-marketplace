from tg_scripting import *
import numpy as np

lookback = input.int(200, "Lookback Period", minval=50, maxval=500)
exhaustion_mult = input.int(15, "Exhaustion Multiplier x10", minval=10, maxval=30)

c = np.array(close)
o = np.array(open)

bull = (c > o).astype(float)
bear = (c < o).astype(float)

n = len(c)
streak_arr = np.zeros(n)
for i in range(n):
    if bull[i]:
        streak_arr[i] = (streak_arr[i - 1] + 1) if i > 0 and streak_arr[i - 1] > 0 else 1.0
    elif bear[i]:
        streak_arr[i] = (streak_arr[i - 1] - 1) if i > 0 and streak_arr[i - 1] < 0 else -1.0

avg_bull = np.full(n, 2.0)
avg_bear = np.full(n, 2.0)
abs_streak = np.abs(streak_arr)
ends = np.diff(np.sign(streak_arr), prepend=0) != 0
for i in range(lookback, n):
    window = streak_arr[i - lookback:i]
    sign_changes = np.where(np.diff(np.sign(window)) != 0)[0]
    bull_lens = []
    bear_lens = []
    prev = 0
    for sc in sign_changes:
        seg = window[prev:sc + 1]
        if seg[0] > 0:
            bull_lens.append(len(seg))
        elif seg[0] < 0:
            bear_lens.append(len(seg))
        prev = sc + 1
    seg = window[prev:]
    if len(seg) > 0 and seg[0] > 0:
        bull_lens.append(len(seg))
    elif len(seg) > 0 and seg[0] < 0:
        bear_lens.append(len(seg))
    if bull_lens:
        avg_bull[i] = np.mean(bull_lens)
    if bear_lens:
        avg_bear[i] = np.mean(bear_lens)

mult = exhaustion_mult / 10.0
bull_threshold = avg_bull * mult
bear_threshold = avg_bear * mult * -1.0

streak = streak_arr
bull_exhaustion = (streak > 0) & (streak >= bull_threshold)
bear_exhaustion = (streak < 0) & (streak <= bear_threshold)

plot(streak, title="Streak", color="#2196F3")
plot(bull_threshold, title="Bull Exhaustion Threshold", color="#4CAF50")
plot(bear_threshold, title="Bear Exhaustion Threshold", color="#F44336")
hline(0, title="Zero", color="#555555")
plotshape(bull_exhaustion, title="Bull Exhaustion", style="triangledown", location="abovebar", color="#FF5722")
plotshape(bear_exhaustion, title="Bear Exhaustion", style="triangleup", location="belowbar", color="#FF5722")
bgcolor(bull_exhaustion, color="rgba(255, 87, 34, 0.15)")
bgcolor(bear_exhaustion, color="rgba(255, 87, 34, 0.15)")
