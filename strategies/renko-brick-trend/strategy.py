# Renko Brick Trend — brick construction plus a trend rule on top of it.
from tg_scripting import *
import numpy as np

indicator("Renko Brick Trend", overlay=True)

brick_mode = input.string("ATR", "Brick size mode", options=["ATR", "Percent"])
atr_length = input.int(14, "ATR length", minval=5, maxval=100)
atr_mult = input.float(1.0, "ATR multiple", minval=0.2, maxval=5.0)
pct_size = input.float(1.0, "Percent brick size", minval=0.1, maxval=10.0)
confirm_bricks = input.int(2, "Bricks needed to flip", minval=1, maxval=5)

c = np.asarray(close, dtype=float)
n = len(c)
atr = ta.atr(high, low, close, atr_length)

brick_level = np.full(n, np.nan)
brick_dir = np.zeros(n)

# Renko ignores time: a brick only prints when price has moved a full brick
# size from the last brick, so many bars produce no brick at all.
last_brick = float(c[0])
direction = 0
run = 0
flip_long = np.zeros(n, dtype=bool)
flip_short = np.zeros(n, dtype=bool)

for i in range(atr_length + 1, n):
    strategy.set_bar_index(i)

    if brick_mode == "ATR":
        size = float(atr[i]) * atr_mult if atr[i] == atr[i] else 0.0
    else:
        size = last_brick * pct_size / 100

    if size <= 0:
        continue

    moved = c[i] - last_brick
    bricks = int(abs(moved) / size)
    if bricks >= 1:
        step = 1 if moved > 0 else -1
        last_brick += step * bricks * size
        if step == direction:
            run += bricks
        else:
            direction = step
            run = bricks

    brick_level[i] = last_brick
    brick_dir[i] = direction

    if direction == 1 and run >= confirm_bricks:
        if not flip_long[i - 1]:
            strategy.entry("Long", strategy.LONG)
            strategy.close("Short")
            flip_long[i] = True
    elif direction == -1 and run >= confirm_bricks:
        if not flip_short[i - 1]:
            strategy.entry("Short", strategy.SHORT)
            strategy.close("Long")
            flip_short[i] = True

plot(brick_level, title="Brick level", color="blue")
plotshape(flip_long, title="Brick flip up", style="triangleup", location="belowbar", color="green")
plotshape(flip_short, title="Brick flip down", style="triangledown", location="abovebar", color="red")
