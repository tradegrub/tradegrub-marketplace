from tg_scripting import *
import numpy as np

indicator("Point and Figure Overlay", overlay=True)

box_size_mode = input.string("ATR", "Box Size Mode", options=["ATR", "Fixed"])
box_size = input.float(1.0, "Box Size (Fixed)", minval=0.01, step=0.1)
atr_length = input.int(14, "ATR Length", minval=5, maxval=50)
reversal_boxes = input.int(3, "Reversal Boxes", minval=1, maxval=5)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(hi)

tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(cl, 1)), np.abs(lo - np.roll(cl, 1))))
tr[0] = hi[0] - lo[0]
atr_arr = np.full(n, np.nan)
if n >= atr_length:
    atr_arr[atr_length - 1] = np.mean(tr[:atr_length])
    for i in range(atr_length, n):
        atr_arr[i] = (atr_arr[i - 1] * (atr_length - 1) + tr[i]) / atr_length

last_atr = box_size
for i in range(n):
    if not np.isnan(atr_arr[i]):
        last_atr = atr_arr[i]

bsize = last_atr if box_size_mode == "ATR" else box_size

columns = []
current_dir = 0
col_bottom = 0.0
col_top = 0.0

if n > 0 and bsize > 0:
    col_bottom = np.floor(lo[0] / bsize) * bsize
    col_top = np.ceil(hi[0] / bsize) * bsize
    current_dir = 1
    col_start = 0

    for i in range(1, n):
        if np.isnan(hi[i]) or np.isnan(lo[i]):
            continue
        bs = bsize
        reversal_dist = reversal_boxes * bs

        if current_dir == 1:
            new_top = np.ceil(hi[i] / bs) * bs
            if new_top > col_top:
                col_top = new_top
            drop = col_top - np.floor(lo[i] / bs) * bs
            if drop >= reversal_dist:
                columns.append((current_dir, col_bottom, col_top, col_start))
                current_dir = -1
                col_top = col_top - bs
                col_bottom = np.floor(lo[i] / bs) * bs
                col_start = i
        else:
            new_bottom = np.floor(lo[i] / bs) * bs
            if new_bottom < col_bottom:
                col_bottom = new_bottom
            rise = np.ceil(hi[i] / bs) * bs - col_bottom
            if rise >= reversal_dist:
                columns.append((current_dir, col_bottom, col_top, col_start))
                current_dir = 1
                col_bottom = col_bottom + bs
                col_top = np.ceil(hi[i] / bs) * bs
                col_start = i

    columns.append((current_dir, col_bottom, col_top, col_start))

for col in columns[-20:]:
    direction, bottom, top, bar_idx = col
    if bar_idx >= n or bsize <= 0:
        continue
    mid_price = (top + bottom) / 2
    lbl = "X" if direction == 1 else "O"
    bar_offset = n - 1 - bar_idx
    label.new(bar_offset, mid_price, lbl)

pnf_trend = np.full(n, np.nan)
for col in columns:
    direction, bottom, top, bar_idx = col
    if bar_idx < n:
        pnf_trend[bar_idx] = (top + bottom) / 2

plot(pnf_trend.tolist(), title="P&F Midpoint", color="rgba(255,255,255,0.3)", linewidth=1)

if len(columns) >= 3 and bsize > 0:
    for ci in range(len(columns) - 2, -1, -1):
        if columns[ci][0] == 1:
            _, x_bot, x_top, _ = columns[ci]
            width_boxes = max(1, int(round((x_top - x_bot) / bsize)))
            hline(x_bot + width_boxes * bsize * 2, title="Bull Target", color="#00BCD4", linestyle="dashed")
            break
    for ci in range(len(columns) - 2, -1, -1):
        if columns[ci][0] == -1:
            _, o_bot, o_top, _ = columns[ci]
            width_boxes = max(1, int(round((o_top - o_bot) / bsize)))
            hline(o_top - width_boxes * bsize * 2, title="Bear Target", color="#FF9800", linestyle="dashed")
            break
