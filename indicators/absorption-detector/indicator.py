from tg_scripting import *
import numpy as np

indicator("Absorption Detector", overlay=False)

length = input.int(20, "Length", minval=5, maxval=100)
threshold = input.float(2.0, "Threshold", minval=1.0, maxval=5.0, step=0.1)

src = np.array(close, dtype=float)
opn = np.array(open, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

body = np.abs(src - opn) + 0.001
absorption_raw = vol / body

sma_vals = np.array(ta.sma(absorption_raw.tolist(), length), dtype=float)
std_vals = np.zeros(n)

for i in range(length, n):
    window = absorption_raw[i - length:i]
    std_vals[i] = float(np.std(window))

normalized = np.where(std_vals > 0, (absorption_raw - sma_vals) / std_vals, 0.0)
normalized = np.nan_to_num(normalized, nan=0.0)

extreme = normalized > threshold
extreme_list = extreme.tolist()

plot(normalized.tolist(), title="Absorption Ratio", color="#2196F3", linewidth=2)
hline(threshold, title="Threshold", color="#FF9800", linestyle="dashed")
hline(0, title="Zero", color="#555555", linestyle="dashed")
bgcolor(extreme_list, color="rgba(33,150,243,0.10)")
plotshape(extreme_list, title="Absorption Event", style="diamond",
          location="abovebar", color="#FF9800")
