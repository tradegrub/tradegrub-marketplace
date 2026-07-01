from tg_scripting import *
import numpy as np

smooth_length = input.int(5, "Smooth Length", minval=1, maxval=50)

sl = int(smooth_length)

high_arr = np.array(high[:], dtype=float)
low_arr = np.array(low[:], dtype=float)
open_arr = np.array(open[:], dtype=float)
close_arr = np.array(close[:], dtype=float)

bar_range = high_arr - low_arr
# Avoid division by zero for doji bars
safe_range = np.where(bar_range < 1e-10, 1e-10, bar_range)

# Bar shape ratios
body_ratio = (close_arr - open_arr) / safe_range
close_position = (close_arr - low_arr) / safe_range

# Composite: body_ratio * directional close position
composite = body_ratio * (2.0 * close_position - 1.0)

# Smooth with EMA
smoothed = ta.ema(composite, sl)

plot(smoothed, title="Bar Shape Osc", color=color.lime)
hline(0, title="Zero", color=color.gray)
hline(0.5, title="Bullish", color=color.green)
hline(-0.5, title="Bearish", color=color.red)
bgcolor(smoothed > 0.5, color="rgba(76,175,80,0.08)")
bgcolor(smoothed < -0.5, color="rgba(255,82,82,0.08)")
