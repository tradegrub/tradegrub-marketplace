from tg_scripting import *
import numpy as np

indicator("Quasimodo Reversal", overlay=True)

zigzag_pct = input.float(3.0, "Zigzag Threshold %", minval=0.5, maxval=15.0, step=0.5)
show_lines = input.bool(True, "Draw Pattern Lines")

cl = np.array(close, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

threshold = zigzag_pct / 100.0

pivots = []
direction = 0
last_hi_idx = 0
last_lo_idx = 0
last_hi_val = hi[0]
last_lo_val = lo[0]

for i in range(1, n):
    if direction <= 0:
        if hi[i] > last_hi_val:
            last_hi_val = hi[i]
            last_hi_idx = i
        if last_hi_val > 0 and (last_hi_val - lo[i]) / last_hi_val >= threshold:
            if direction < 0 or len(pivots) == 0:
                pivots.append((last_hi_idx, float(last_hi_val), 1))
            direction = 1
            last_lo_val = lo[i]
            last_lo_idx = i

    if direction >= 0:
        if lo[i] < last_lo_val:
            last_lo_val = lo[i]
            last_lo_idx = i
        if last_lo_val > 0 and (hi[i] - last_lo_val) / last_lo_val >= threshold:
            if direction > 0 or len(pivots) == 0:
                pivots.append((last_lo_idx, float(last_lo_val), -1))
            direction = -1
            last_hi_val = hi[i]
            last_hi_idx = i

# QML: need at least 5 pivots (H, L, HH, LL pattern or L, H, LL, HH pattern)
for i in range(4, len(pivots)):
    p0_idx, p0_val, p0_dir = pivots[i - 4]
    p1_idx, p1_val, p1_dir = pivots[i - 3]
    p2_idx, p2_val, p2_dir = pivots[i - 2]
    p3_idx, p3_val, p3_dir = pivots[i - 1]
    p4_idx, p4_val, p4_dir = pivots[i]

    # Bullish QML: H(+), L(-), HH(+), LL(-), price rises
    # p0=high, p1=low, p2=higher high, p3=lower low (below p1)
    if p0_dir == 1 and p1_dir == -1 and p2_dir == 1 and p3_dir == -1:
        if p2_val > p0_val and p3_val < p1_val:
            label.new(
                x=p3_idx, y=float(lo[p3_idx]),
                text="QML",
                style=label.style_label_up,
                color="rgba(38,166,154,0.4)",
                textcolor="#26a69a",
                size="small"
            )
            if show_lines:
                line.new(x1=p0_idx, y1=p0_val, x2=p2_idx, y2=p2_val,
                         color="rgba(38,166,154,0.5)", width=1, style=line.style_dotted)
                line.new(x1=p1_idx, y1=p1_val, x2=p3_idx, y2=p3_val,
                         color="rgba(38,166,154,0.5)", width=1, style=line.style_dotted)

    # Bearish QML: L(-), H(+), LL(-), HH(+) — but actually:
    # p0=low, p1=high, p2=lower low, p3=higher high (above p1)
    if p0_dir == -1 and p1_dir == 1 and p2_dir == -1 and p3_dir == 1:
        if p2_val < p0_val and p3_val > p1_val:
            label.new(
                x=p3_idx, y=float(hi[p3_idx]),
                text="QML",
                style=label.style_label_down,
                color="rgba(239,83,80,0.4)",
                textcolor="#ef5350",
                size="small"
            )
            if show_lines:
                line.new(x1=p0_idx, y1=p0_val, x2=p2_idx, y2=p2_val,
                         color="rgba(239,83,80,0.5)", width=1, style=line.style_dotted)
                line.new(x1=p1_idx, y1=p1_val, x2=p3_idx, y2=p3_val,
                         color="rgba(239,83,80,0.5)", width=1, style=line.style_dotted)
