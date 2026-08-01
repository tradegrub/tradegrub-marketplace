from tg_scripting import *
import numpy as np

indicator("Bar Efficiency Ratio", overlay=False)

smooth_length = input.int(10, "Smooth Length", minval=2, maxval=50)

src = np.array(close, dtype=float)
opn = np.array(open, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

bar_range = hi - lo + 0.001
body = np.abs(src - opn)
efficiency = body / bar_range

smoothed = np.array(ta.sma(efficiency.tolist(), smooth_length), dtype=float)

plot(efficiency.tolist(), title="Efficiency", color="#7E57C2", linewidth=1)
plot(smoothed.tolist(), title="Smoothed", color="#FF9800", linewidth=2)
hline(0.7, title="Directional", color="#4CAF50", linestyle="dashed")
hline(0.3, title="Indecisive", color="#f44336", linestyle="dashed")
