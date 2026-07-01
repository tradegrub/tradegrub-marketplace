from tg_scripting import *
import numpy as np
from scipy.signal import argrelextrema

indicator("Swing Fibonacci Mapper", overlay=True)

order = input.int(15, "Swing Order", minval=5, maxval=40)
show_ext = input.bool(True, "Show Extensions")

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

peaks = argrelextrema(hi, np.greater_equal, order=order)[0]
troughs = argrelextrema(lo, np.less_equal, order=order)[0]

fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
fib_ext = [1.272, 1.618]
fib_colors = ["#4CAF50", "#66bb6a", "#42a5f5", "#29b6f6", "#ab47bc", "#e040fb", "#ef5350"]
ext_colors = ["#ff9800", "#ffca28"]

if len(peaks) > 0 and len(troughs) > 0:
    last_peak = peaks[-1]
    last_trough = troughs[-1]

    if last_peak > last_trough:
        swing_lo = float(lo[last_trough])
        swing_hi = float(hi[last_peak])
        start_bar = last_trough
        end_bar = last_peak
    else:
        swing_lo = float(lo[last_trough])
        swing_hi = float(hi[last_peak])
        start_bar = last_peak
        end_bar = last_trough

    rng = swing_hi - swing_lo

    for idx, fib in enumerate(fib_levels):
        if last_peak > last_trough:
            level = swing_hi - rng * fib
        else:
            level = swing_lo + rng * fib

        color = fib_colors[idx]
        line.new(x1=start_bar, y1=level, x2=n-1, y2=level,
                 color=color, width=1, style=line.style_dashed)
        label.new(x=n-1, y=level,
                  text=f"{fib:.3f} ({level:.2f})",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor=color, size="tiny")

    if show_ext:
        for idx, fib in enumerate(fib_ext):
            if last_peak > last_trough:
                level = swing_hi - rng * fib
            else:
                level = swing_lo + rng * fib
            color = ext_colors[idx]
            line.new(x1=end_bar, y1=level, x2=n-1, y2=level,
                     color=color, width=1, style=line.style_dashed)
            label.new(x=n-1, y=level,
                      text=f"{fib:.3f} ext ({level:.2f})",
                      style=label.style_label_left, color="rgba(0,0,0,0)",
                      textcolor=color, size="tiny")

    label.new(x=last_peak, y=float(hi[last_peak]),
              text="Swing High", style=label.style_label_down,
              color="#ef5350", textcolor="#ffffff", size="small")
    label.new(x=last_trough, y=float(lo[last_trough]),
              text="Swing Low", style=label.style_label_up,
              color="#4CAF50", textcolor="#ffffff", size="small")
