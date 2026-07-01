from tg_scripting import *
import numpy as np

indicator("Volume Rate of Change", overlay=False)

length = input.int(14, "Length", minval=1, maxval=100)
smooth_len = input.int(3, "Smoothing", minval=1, maxval=20)
upper_thresh = input.float(50.0, "Upper Threshold %", minval=10.0, maxval=500.0, step=10.0)

vol_arr = np.array(volume, dtype=float)
n = len(vol_arr)

vroc = np.zeros(n)
for i in range(length, n):
    if vol_arr[i - length] != 0:
        vroc[i] = ((vol_arr[i] - vol_arr[i - length]) / vol_arr[i - length]) * 100.0

vroc_smooth = ta.sma(vroc.tolist(), smooth_len)

spike_up = (vroc > upper_thresh).tolist()

plot(vroc.tolist(), title="VROC", color="#42A5F5", linewidth=1)
plot(vroc_smooth, title="VROC Smooth", color="#FFA726", linewidth=2)
hline(0.0, title="Zero", color="#555555", linestyle="dashed")
hline(upper_thresh, title="Upper", color="#00e676", linestyle="dashed")
hline(-upper_thresh, title="Lower", color="#ff1744", linestyle="dashed")
plotshape(spike_up, title="Volume Spike", style="triangleup", location="bottom", color="#00e676")
