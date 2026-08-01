from tg_scripting import *
import numpy as np

indicator("Fractal Pivot Levels", overlay=True)

period = input.int(5, "Fractal Period", minval=2, maxval=20)
max_levels = input.int(5, "Max Levels", minval=1, maxval=10)
show_labels = input.bool(True, "Show Labels")

src_h = np.array(high, dtype=float)
src_l = np.array(low, dtype=float)
src_c = np.array(close, dtype=float)
n = len(src_c)

frac_high = np.full(n, np.nan)
frac_low = np.full(n, np.nan)
res_level = np.full(n, np.nan)
sup_level = np.full(n, np.nan)

highs_list = []
lows_list = []

for i in range(period, n - period):
    is_high = True
    is_low = True
    for j in range(1, period + 1):
        if src_h[i] <= src_h[i - j] or src_h[i] <= src_h[i + j]:
            is_high = False
        if src_l[i] >= src_l[i - j] or src_l[i] >= src_l[i + j]:
            is_low = False

    if is_high:
        frac_high[i] = src_h[i]
        highs_list.append((i, src_h[i]))
    if is_low:
        frac_low[i] = src_l[i]
        lows_list.append((i, src_l[i]))

recent_res = []
recent_sup = []

for i in range(n):
    while recent_res and len(recent_res) > max_levels:
        recent_res.pop(0)
    while recent_sup and len(recent_sup) > max_levels:
        recent_sup.pop(0)

    if not np.isnan(frac_high[i]):
        recent_res.append(frac_high[i])
    if not np.isnan(frac_low[i]):
        recent_sup.append(frac_low[i])

    if recent_res:
        closest_r = min(recent_res, key=lambda x: abs(x - src_c[i]))
        res_level[i] = closest_r
    if recent_sup:
        closest_s = min(recent_sup, key=lambda x: abs(x - src_c[i]))
        sup_level[i] = closest_s

for idx, val in highs_list[-max_levels:]:
    if idx < n - 1:
        line.new(x1=idx, y1=val, x2=n - 1, y2=val,
                 color="rgba(239,83,80,0.5)", width=1, style=line.style_dashed)
        if show_labels:
            label.new(x=idx, y=val, text="R",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#FFFFFF", size="tiny")

for idx, val in lows_list[-max_levels:]:
    if idx < n - 1:
        line.new(x1=idx, y1=val, x2=n - 1, y2=val,
                 color="rgba(76,175,80,0.5)", width=1, style=line.style_dashed)
        if show_labels:
            label.new(x=idx, y=val, text="S",
                      style=label.style_label_up, color="#4CAF50",
                      textcolor="#FFFFFF", size="tiny")

plotshape(~np.isnan(frac_high), title="Fractal High", style="triangledown",
          location="abovebar", color="#ef5350")
plotshape(~np.isnan(frac_low), title="Fractal Low", style="triangleup",
          location="belowbar", color="#4CAF50")
plot(res_level, title="Nearest Resistance", color="rgba(239,83,80,0.3)", linewidth=1)
plot(sup_level, title="Nearest Support", color="rgba(76,175,80,0.3)", linewidth=1)
