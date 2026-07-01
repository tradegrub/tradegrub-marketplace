from tg_scripting import *
import numpy as np

indicator("Measured Move Projector", overlay=True)

swing_len = input.int(10, "Swing Length", minval=3, maxval=50)
tolerance = input.float(10.0, "CD Tolerance %", minval=1.0, maxval=30.0, step=1.0)
show_targets = input.bool(True, "Show Targets")

src_h = np.array(high, dtype=float)
src_l = np.array(low, dtype=float)
src_c = np.array(close, dtype=float)
n = len(src_c)

proj_up = np.full(n, np.nan)
proj_dn = np.full(n, np.nan)
signal = np.full(n, 0.0)

def find_swings(data, length, find_high=True):
    swings = []
    for i in range(length, len(data) - length):
        window = data[i - length:i + length + 1]
        if find_high and data[i] == np.max(window):
            swings.append((i, data[i]))
        elif not find_high and data[i] == np.min(window):
            swings.append((i, data[i]))
    return swings

swing_highs = find_swings(src_h, swing_len, True)
swing_lows = find_swings(src_l, swing_len, False)

all_swings = [(i, v, 'H') for i, v in swing_highs] + [(i, v, 'L') for i, v in swing_lows]
all_swings.sort(key=lambda x: x[0])

for idx in range(3, len(all_swings)):
    a_i, a_v, a_t = all_swings[idx - 3]
    b_i, b_v, b_t = all_swings[idx - 2]
    c_i, c_v, c_t = all_swings[idx - 1]
    d_i, d_v, d_t = all_swings[idx]

    if a_t == 'L' and b_t == 'H' and c_t == 'L' and d_t == 'H':
        ab = b_v - a_v
        cd = d_v - c_v
        if ab > 0 and cd > 0:
            ratio = abs(cd / ab - 1.0) * 100.0
            if ratio < tolerance:
                target = c_v + ab
                if d_i < n:
                    proj_up[d_i] = target
                    signal[d_i] = 1.0
                    line.new(x1=a_i, y1=a_v, x2=b_i, y2=b_v,
                             color="#42A5F5", width=2, style=line.style_solid)
                    line.new(x1=c_i, y1=c_v, x2=d_i, y2=d_v,
                             color="#42A5F5", width=2, style=line.style_solid)
                    line.new(x1=b_i, y1=b_v, x2=c_i, y2=c_v,
                             color="#42A5F5", width=1, style=line.style_dashed)
                    if show_targets:
                        line.new(x1=d_i, y1=target, x2=min(d_i + 10, n - 1),
                                 y2=target, color="#00e676", width=1, style=line.style_dashed)
                        label.new(x=d_i, y=target, text="T:" + str(round(target, 2)),
                                  style=label.style_label_left, color="#00e676",
                                  textcolor="#000000", size="small")

    if a_t == 'H' and b_t == 'L' and c_t == 'H' and d_t == 'L':
        ab = a_v - b_v
        cd = c_v - d_v
        if ab > 0 and cd > 0:
            ratio = abs(cd / ab - 1.0) * 100.0
            if ratio < tolerance:
                target = c_v - ab
                if d_i < n:
                    proj_dn[d_i] = target
                    signal[d_i] = -1.0
                    line.new(x1=a_i, y1=a_v, x2=b_i, y2=b_v,
                             color="#ef5350", width=2, style=line.style_solid)
                    line.new(x1=c_i, y1=c_v, x2=d_i, y2=d_v,
                             color="#ef5350", width=2, style=line.style_solid)
                    line.new(x1=b_i, y1=b_v, x2=c_i, y2=c_v,
                             color="#ef5350", width=1, style=line.style_dashed)
                    if show_targets:
                        line.new(x1=d_i, y1=target, x2=min(d_i + 10, n - 1),
                                 y2=target, color="#ef5350", width=1, style=line.style_dashed)
                        label.new(x=d_i, y=target, text="T:" + str(round(target, 2)),
                                  style=label.style_label_left, color="#ef5350",
                                  textcolor="#FFFFFF", size="small")

plot(signal, title="MM Signal", color="#AB47BC", linewidth=1)
