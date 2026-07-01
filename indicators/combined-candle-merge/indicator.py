from tg_scripting import *
import numpy as np

indicator("Combined Candle Merge", overlay=True)

min_candles = input.int(2, "Min Candles to Merge", minval=2, maxval=10)
show_wicks = input.bool(True, "Show Merged Wicks")
bull_color = "rgba(38,166,154,0.4)"
bear_color = "rgba(239,83,80,0.4)"

cl = np.array(close, dtype=np.float64)
op = np.array(open, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

i = 0
while i < n:
    is_bull = cl[i] >= op[i]
    start = i
    j = i + 1

    while j < n:
        next_bull = cl[j] >= op[j]
        if next_bull != is_bull:
            break
        j += 1

    run_len = j - start

    if run_len >= min_candles:
        merged_open = float(op[start])
        merged_close = float(cl[j - 1])
        merged_high = float(np.max(hi[start:j]))
        merged_low = float(np.min(lo[start:j]))

        box_top = max(merged_open, merged_close)
        box_bottom = min(merged_open, merged_close)
        color = bull_color if is_bull else bear_color

        box.new(
            left=start, top=box_top,
            right=j - 1, bottom=box_bottom,
            bgcolor=color,
            border_color="#26a69a" if is_bull else "#ef5350",
            border_width=1
        )

        if show_wicks:
            mid_x = (start + j - 1) // 2
            if merged_high > box_top:
                line.new(
                    x1=mid_x, y1=box_top,
                    x2=mid_x, y2=merged_high,
                    color="#26a69a" if is_bull else "#ef5350",
                    width=1
                )
            if merged_low < box_bottom:
                line.new(
                    x1=mid_x, y1=box_bottom,
                    x2=mid_x, y2=merged_low,
                    color="#26a69a" if is_bull else "#ef5350",
                    width=1
                )

        label.new(
            x=mid_x, y=merged_high if is_bull else merged_low,
            text=str(run_len),
            style=label.style_label_down if is_bull else label.style_label_up,
            color="rgba(0,0,0,0)",
            textcolor="#26a69a" if is_bull else "#ef5350",
            size="tiny"
        )

    i = j
