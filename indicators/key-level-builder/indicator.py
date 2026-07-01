from tg_scripting import *
import numpy as np
from scipy.signal import argrelextrema

indicator("Key Level Builder", overlay=True)

order = input.int(10, "Pivot Order", minval=3, maxval=30)
num_levels = input.int(5, "Number of Levels", minval=2, maxval=10)
zone_atr_mult = input.float(0.5, "Zone Width (ATR)", minval=0.1, maxval=2.0, step=0.1)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, 14), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)
avg_atr = float(np.mean(atr_arr[14:]))

peak_idx = argrelextrema(hi, np.greater_equal, order=order)[0]
trough_idx = argrelextrema(lo, np.less_equal, order=order)[0]

pivots = []
for i in peak_idx:
    pivots.append(float(hi[i]))
for i in trough_idx:
    pivots.append(float(lo[i]))

if len(pivots) < 2:
    plot(cl.tolist(), title="Close", color="#ffffff")
else:
    pivots = sorted(pivots)
    clusters = []
    current = [pivots[0]]
    for p in pivots[1:]:
        if p - current[-1] < avg_atr * zone_atr_mult:
            current.append(p)
        else:
            clusters.append(current)
            current = [p]
    clusters.append(current)

    clusters.sort(key=lambda c: -len(c))
    top_levels = clusters[:num_levels]

    colors_res = ["#ef5350", "#ff7043", "#ffa726", "#ffca28", "#ffee58"]
    colors_sup = ["#4CAF50", "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9"]

    for idx, cluster in enumerate(top_levels):
        level = float(np.mean(cluster))
        width = avg_atr * zone_atr_mult
        color = colors_res[idx] if level > cl[-1] else colors_sup[idx]

        hline(level, title=f"Level {idx+1}", color=color)
        box.new(
            left=n-80, top=level + width/2, right=n-1, bottom=level - width/2,
            border_color=color, bgcolor=f"rgba(128,128,128,0.08)"
        )
        label.new(
            x=n-40, y=level,
            text=f"{'R' if level > cl[-1] else 'S'}{idx+1}: {level:.2f} ({len(cluster)}x)",
            style=label.style_none, color=color, textcolor=color, size="small"
        )
