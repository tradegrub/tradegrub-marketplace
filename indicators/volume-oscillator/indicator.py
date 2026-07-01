from tg_scripting import *
import numpy as np

indicator("Volume Oscillator", overlay=False)

fast_len = input.int(5, "Fast Length", minval=1, maxval=50)
slow_len = input.int(20, "Slow Length", minval=5, maxval=200)
show_hist = input.bool(True, "Show Histogram")

vol_fast = ta.ema(volume, fast_len)
vol_slow = ta.ema(volume, slow_len)

vol_fast_arr = np.array(vol_fast, dtype=float)
vol_slow_arr = np.array(vol_slow, dtype=float)

vo = np.where(vol_slow_arr != 0, ((vol_fast_arr - vol_slow_arr) / vol_slow_arr) * 100.0, 0.0)

plot(vo.tolist(), title="Volume Oscillator", color="#42A5F5", linewidth=2)
hline(0.0, title="Zero", color="#555555", linestyle="dashed")

if show_hist:
    hist_color = np.where(vo > 0, "#66BB6A", "#EF5350")
    plot(vo.tolist(), title="Histogram", color=hist_color.tolist(), style=plot.style_histogram)
