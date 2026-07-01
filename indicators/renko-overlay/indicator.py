from tg_scripting import *
import numpy as np

indicator("Renko Overlay", overlay=True)

brick_size_mode = input.string("ATR", "Brick Size Mode", options=["ATR", "Fixed"])
brick_size = input.float(1.0, "Fixed Brick Size", minval=0.01, step=0.1)
atr_length = input.int(14, "ATR Length", minval=1, maxval=200)
atr_mult = input.float(1.0, "ATR Multiplier", minval=0.1, maxval=10.0, step=0.1)

n = len(close)
close_arr = np.array(close, dtype=np.float64)
high_arr = np.array(high, dtype=np.float64)
low_arr = np.array(low, dtype=np.float64)

tr_arr = np.maximum(
    high_arr - low_arr,
    np.maximum(
        np.abs(high_arr - np.roll(close_arr, 1)),
        np.abs(low_arr - np.roll(close_arr, 1))
    )
)
tr_arr[0] = high_arr[0] - low_arr[0]
atr_vals = np.full(n, np.nan)
if n >= atr_length:
    atr_vals[atr_length - 1] = np.mean(tr_arr[:atr_length])
    for i in range(atr_length, n):
        atr_vals[i] = (atr_vals[i - 1] * (atr_length - 1) + tr_arr[i]) / atr_length

brick_tops = np.full(n, np.nan)
brick_bottoms = np.full(n, np.nan)
brick_dirs = np.zeros(n, dtype=np.int32)
trend_line = np.full(n, np.nan)

start_idx = 0
if brick_size_mode == "ATR":
    start_idx = atr_length - 1
    while start_idx < n and np.isnan(atr_vals[start_idx]):
        start_idx += 1

if start_idx >= n:
    plot(close_arr.tolist(), title="Renko Trend", color="#FFD700")
else:
    current_bs = brick_size if brick_size_mode == "Fixed" else atr_vals[start_idx] * atr_mult
    if current_bs <= 0:
        current_bs = 1.0

    ref_price = round(close_arr[start_idx] / current_bs) * current_bs
    last_top = ref_price + current_bs / 2
    last_bottom = ref_price - current_bs / 2
    last_dir = 0

    for i in range(start_idx, n):
        if brick_size_mode == "ATR" and not np.isnan(atr_vals[i]):
            current_bs = max(atr_vals[i] * atr_mult, 0.01)

        price = close_arr[i]
        bricks_formed = False

        if last_dir >= 0:
            while price >= last_top + current_bs:
                last_bottom = last_top
                last_top = last_bottom + current_bs
                last_dir = 1
                bricks_formed = True
            if price <= last_bottom - 2 * current_bs:
                last_top = last_bottom
                last_bottom = last_top - current_bs
                last_dir = -1
                bricks_formed = True
                while price <= last_bottom - current_bs:
                    last_top = last_bottom
                    last_bottom = last_top - current_bs

        if last_dir < 0 and not bricks_formed:
            while price <= last_bottom - current_bs:
                last_top = last_bottom
                last_bottom = last_top - current_bs
                last_dir = -1
                bricks_formed = True
            if price >= last_top + 2 * current_bs:
                last_bottom = last_top
                last_top = last_bottom + current_bs
                last_dir = 1
                bricks_formed = True
                while price >= last_top + current_bs:
                    last_bottom = last_top
                    last_top = last_bottom + current_bs

        brick_tops[i] = last_top
        brick_bottoms[i] = last_bottom
        brick_dirs[i] = last_dir
        trend_line[i] = (last_top + last_bottom) / 2

        if bricks_formed:
            bc = "#4CAF50" if last_dir == 1 else "#EF5350"
            box.new(i - 1, last_top, i, last_bottom, border_color=bc, bgcolor=bc)

    plot(trend_line.tolist(), title="Renko Trend", color="#FFD700", linewidth=2)

    bgcolor(brick_dirs > 0, color="rgba(76,175,80,0.08)")
    bgcolor(brick_dirs < 0, color="rgba(239,83,80,0.08)")
