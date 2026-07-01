from tg_scripting import *
import numpy as np

indicator("Double Top Bottom Detector", overlay=True)

lookback = input.int(30, "Lookback Period", minval=10, maxval=100)
tolerance = input.float(1.5, "Price Tolerance %", minval=0.5, maxval=5.0, step=0.1)
min_gap = input.int(5, "Min Bars Between Peaks", minval=3, maxval=30)
confirm_bars = input.int(3, "Confirmation Bars", minval=1, maxval=10)

h = np.array(high, dtype=float)
l = np.array(low, dtype=float)
c = np.array(close, dtype=float)
n = len(c)

double_top = np.zeros(n, dtype=bool)
double_bottom = np.zeros(n, dtype=bool)
neckline_val = np.zeros(n)

for i in range(lookback + confirm_bars, n):
    window_h = h[i - lookback:i]
    window_l = l[i - lookback:i]

    # Find highest points for double top
    peak1_idx = np.argmax(window_h)
    peak1_val = window_h[peak1_idx]

    # Mask around peak1 and find second peak
    mask = np.ones(len(window_h), dtype=bool)
    start_m = max(0, peak1_idx - min_gap)
    end_m = min(len(window_h), peak1_idx + min_gap + 1)
    mask[start_m:end_m] = False
    masked_h = np.where(mask, window_h, 0)

    if np.any(masked_h > 0):
        peak2_idx = np.argmax(masked_h)
        peak2_val = masked_h[peak2_idx]

        pct_diff = abs(peak1_val - peak2_val) / peak1_val * 100
        if pct_diff < tolerance and abs(peak1_idx - peak2_idx) >= min_gap:
            trough_start = min(peak1_idx, peak2_idx)
            trough_end = max(peak1_idx, peak2_idx)
            neckline = np.min(window_l[trough_start:trough_end + 1])
            if c[i] < neckline and all(c[i - j] >= neckline for j in range(1, confirm_bars + 1)):
                double_top[i] = True
                neckline_val[i] = neckline

    # Find lowest points for double bottom
    valley1_idx = np.argmin(window_l)
    valley1_val = window_l[valley1_idx]

    mask2 = np.ones(len(window_l), dtype=bool)
    start_m2 = max(0, valley1_idx - min_gap)
    end_m2 = min(len(window_l), valley1_idx + min_gap + 1)
    mask2[start_m2:end_m2] = False
    masked_l = np.where(mask2, window_l, np.inf)

    if np.any(np.isfinite(masked_l)):
        valley2_idx = np.argmin(masked_l)
        valley2_val = masked_l[valley2_idx]

        if valley1_val > 0:
            pct_diff2 = abs(valley1_val - valley2_val) / valley1_val * 100
            if pct_diff2 < tolerance and abs(valley1_idx - valley2_idx) >= min_gap:
                peak_start = min(valley1_idx, valley2_idx)
                peak_end = max(valley1_idx, valley2_idx)
                neckline2 = np.max(window_h[peak_start:peak_end + 1])
                if c[i] > neckline2 and all(c[i - j] <= neckline2 for j in range(1, confirm_bars + 1)):
                    double_bottom[i] = True
                    neckline_val[i] = neckline2

plotshape(double_top, title="Double Top", style="triangledown", location="abovebar", color="#FF5252")
plotshape(double_bottom, title="Double Bottom", style="triangleup", location="belowbar", color="#00e676")
plot(neckline_val.tolist(), title="Neckline", color="#42A5F5", linewidth=1)
bgcolor(double_top, color="rgba(239,83,80,0.08)")
bgcolor(double_bottom, color="rgba(0,230,118,0.08)")
