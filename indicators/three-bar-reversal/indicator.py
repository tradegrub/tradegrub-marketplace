from tg_scripting import *
import numpy as np

indicator("Three Bar Reversal Detector", overlay=True)

min_body_pct = input.float(0.5, "Min Body % of Range", minval=0.2, maxval=0.9, step=0.05)
show_soldiers = input.bool(True, "Show Three White Soldiers")
show_crows = input.bool(True, "Show Three Black Crows")
show_inside = input.bool(True, "Show Three Inside Up/Down")

o = np.array(open, dtype=float)
h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

body = np.abs(c - o)
rng = h - l
rng = np.where(rng == 0, 0.0001, rng)
body_ratio = body / rng
bullish = c > o
bearish = c < o

soldiers = np.zeros(n, dtype=bool)
crows = np.zeros(n, dtype=bool)
inside_up = np.zeros(n, dtype=bool)
inside_down = np.zeros(n, dtype=bool)

for i in range(2, n):
    # Three White Soldiers
    if show_soldiers:
        if (bullish[i] and bullish[i-1] and bullish[i-2] and
            body_ratio[i] > min_body_pct and body_ratio[i-1] > min_body_pct and body_ratio[i-2] > min_body_pct and
            c[i] > c[i-1] > c[i-2] and
            o[i] > o[i-1] > o[i-2] and
            o[i] < c[i-1] and o[i-1] < c[i-2]):
            soldiers[i] = True

    # Three Black Crows
    if show_crows:
        if (bearish[i] and bearish[i-1] and bearish[i-2] and
            body_ratio[i] > min_body_pct and body_ratio[i-1] > min_body_pct and body_ratio[i-2] > min_body_pct and
            c[i] < c[i-1] < c[i-2] and
            o[i] < o[i-1] < o[i-2] and
            o[i] > c[i-1] and o[i-1] > c[i-2]):
            crows[i] = True

    # Three Inside Up
    if show_inside:
        if (bearish[i-2] and bullish[i-1] and bullish[i] and
            o[i-1] > c[i-2] and c[i-1] < o[i-2] and
            body[i-1] < body[i-2] * 0.6 and
            c[i] > o[i-2]):
            inside_up[i] = True

    # Three Inside Down
    if show_inside:
        if (bullish[i-2] and bearish[i-1] and bearish[i] and
            o[i-1] < c[i-2] and c[i-1] > o[i-2] and
            body[i-1] < body[i-2] * 0.6 and
            c[i] < o[i-2]):
            inside_down[i] = True

bull_any = soldiers | inside_up
bear_any = crows | inside_down

plotshape(soldiers, title="Three White Soldiers", style="triangleup", location="belowbar", color="#00e676")
plotshape(crows, title="Three Black Crows", style="triangledown", location="abovebar", color="#FF5252")
plotshape(inside_up, title="Three Inside Up", style="triangleup", location="belowbar", color="#66BB6A")
plotshape(inside_down, title="Three Inside Down", style="triangledown", location="abovebar", color="#EF5350")

score = np.where(soldiers, 2.0, np.where(inside_up, 1.0, np.where(crows, -2.0, np.where(inside_down, -1.0, 0.0))))
plot(score.tolist(), title="Pattern Score", color="#42A5F5", linewidth=1)
