from tg_scripting import *
import numpy as np

indicator("Overnight Gap Analyzer", overlay=False)

gap_thresh = input.float(0.3, "Min Gap %", minval=0.05, maxval=5.0, step=0.05)
lookback = input.int(50, "Lookback Bars", minval=10, maxval=200)
show_labels = input.bool(True, "Show Gap Labels")

src_c = np.array(close, dtype=float)
src_o = np.array(open, dtype=float)
src_h = np.array(high, dtype=float)
src_l = np.array(low, dtype=float)
n = len(src_c)

gap_pct = np.full(n, 0.0)
fill_rate = np.full(n, np.nan)
avg_gap = np.full(n, np.nan)
gap_direction = np.full(n, 0.0)

gap_up_list = []
gap_dn_list = []

for i in range(1, n):
    g = (src_o[i] - src_c[i - 1]) / (src_c[i - 1] + 1e-10) * 100.0
    if abs(g) >= gap_thresh:
        gap_pct[i] = g

        filled = False
        if g > 0:
            gap_up_list.append(i)
            gap_direction[i] = 1.0
            if src_l[i] <= src_c[i - 1]:
                filled = True
        else:
            gap_dn_list.append(i)
            gap_direction[i] = -1.0
            if src_h[i] >= src_c[i - 1]:
                filled = True

        if not filled:
            for k in range(i + 1, min(i + 20, n)):
                if g > 0 and src_l[k] <= src_c[i - 1]:
                    filled = True
                    break
                elif g < 0 and src_h[k] >= src_c[i - 1]:
                    filled = True
                    break

for i in range(lookback, n):
    gaps_in_window = []
    fills_in_window = 0
    for j in range(i - lookback, i):
        if abs(gap_pct[j]) >= gap_thresh:
            gaps_in_window.append(gap_pct[j])

            g = gap_pct[j]
            filled = False
            if g > 0:
                for k in range(j, min(j + 20, i)):
                    if src_l[k] <= src_c[max(0, j - 1)]:
                        filled = True
                        break
            else:
                for k in range(j, min(j + 20, i)):
                    if src_h[k] >= src_c[max(0, j - 1)]:
                        filled = True
                        break
            if filled:
                fills_in_window += 1

    if len(gaps_in_window) > 0:
        avg_gap[i] = np.mean(np.abs(gaps_in_window))
        fill_rate[i] = fills_in_window / len(gaps_in_window) * 100.0

if show_labels:
    for i in range(1, n):
        if gap_pct[i] > gap_thresh:
            label.new(x=i, y=gap_pct[i], text="G+",
                      style=label.style_label_down, color="#4CAF50",
                      textcolor="#FFFFFF", size="tiny")
        elif gap_pct[i] < -gap_thresh:
            label.new(x=i, y=gap_pct[i], text="G-",
                      style=label.style_label_up, color="#ef5350",
                      textcolor="#FFFFFF", size="tiny")

plot(gap_pct, title="Gap %", color="#AB47BC", linewidth=2)
plot(fill_rate, title="Fill Rate %", color="#42A5F5", linewidth=1)
plot(avg_gap, title="Avg Gap Size %", color="#FFA726", linewidth=1)

hline(0, title="Zero", color="#555", linestyle="dashed")
hline(50, title="50% Fill", color="rgba(66,165,245,0.3)", linestyle="dashed")
