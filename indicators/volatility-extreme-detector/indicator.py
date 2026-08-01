from tg_scripting import *
import numpy as np

indicator("Volatility Extreme Detector", overlay=False)

period = input.int(22, "Lookback Period", minval=5, maxval=100)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)
threshold = input.float(1.5, "Extreme Threshold (StdDev)", minval=0.5, maxval=4.0, step=0.25)

cl = np.array(close, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

# Williams Vix Fix: (highest close over period - low) / highest close
wvf = np.full(n, 0.0)
wvf_inv = np.full(n, 0.0)

for i in range(period, n):
    highest_close = np.max(cl[i - period:i + 1])
    lowest_close = np.min(cl[i - period:i + 1])
    if highest_close > 0:
        wvf[i] = (highest_close - lo[i]) / highest_close * 100.0
    if lowest_close > 0:
        wvf_inv[i] = (hi[i] - lowest_close) / lowest_close * 100.0

# Smooth
if smooth > 1:
    kernel = np.ones(smooth) / smooth
    wvf_smooth = np.convolve(wvf, kernel, mode='same')
    wvf_inv_smooth = np.convolve(wvf_inv, kernel, mode='same')
else:
    wvf_smooth = wvf.copy()
    wvf_inv_smooth = wvf_inv.copy()

# Dynamic thresholds
wvf_upper = np.full(n, 0.0)
wvf_inv_upper = np.full(n, 0.0)

for i in range(period, n):
    w = wvf_smooth[i - period:i + 1]
    wvf_upper[i] = np.mean(w) + threshold * np.std(w)
    w2 = wvf_inv_smooth[i - period:i + 1]
    wvf_inv_upper[i] = np.mean(w2) + threshold * np.std(w2)

bottom_signal = np.zeros(n, dtype=bool)
top_signal = np.zeros(n, dtype=bool)

for i in range(period, n):
    if wvf_smooth[i] > wvf_upper[i]:
        bottom_signal[i] = True
    if wvf_inv_smooth[i] > wvf_inv_upper[i]:
        top_signal[i] = True

plot(wvf_smooth.tolist(), title="Bottom Volatility", color="#26a69a", linewidth=2)
plot((-wvf_inv_smooth).tolist(), title="Top Volatility", color="#ef5350", linewidth=2)
hline(0, title="Zero", color="rgba(158,158,158,0.4)")

plotshape(bottom_signal.tolist(), title="Extreme Bottom", style="triangleup",
          location="belowbar", color="#00e676", size="small")
plotshape(top_signal.tolist(), title="Extreme Top", style="triangledown",
          location="abovebar", color="#ff1744", size="small")

bgcolor(bottom_signal, color="rgba(0,230,118,0.08)")
bgcolor(top_signal, color="rgba(255,23,68,0.08)")
