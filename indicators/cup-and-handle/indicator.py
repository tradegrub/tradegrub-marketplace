from tg_scripting import *
import numpy as np

indicator("Cup and Handle Detector", overlay=True)

cup_len = input.int(30, "Cup Length", minval=10, maxval=100)
handle_len = input.int(10, "Handle Length", minval=3, maxval=30)
depth_pct = input.float(5.0, "Min Depth %", minval=1.0, maxval=20.0, step=0.5)
show_labels = input.bool(True, "Show Labels")

try:
    from scipy.optimize import curve_fit
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

src = np.array(close, dtype=float)
n = len(src)

cup_signal = np.full(n, False)
handle_signal = np.full(n, False)
cup_top = np.full(n, np.nan)
cup_bot = np.full(n, np.nan)

def parabola(x, a, b, c):
    return a * x * x + b * x + c

def fit_score(segment):
    if not HAS_SCIPY:
        return 1.0, 0.0
    xs = np.arange(len(segment), dtype=float)
    try:
        popt, _ = curve_fit(parabola, xs, segment, maxfev=2000)
        fitted = parabola(xs, *popt)
        ss_res = np.sum((segment - fitted) ** 2)
        ss_tot = np.sum((segment - np.mean(segment)) ** 2)
        r2 = 1.0 - ss_res / (ss_tot + 1e-10)
        return r2, popt[0]
    except Exception:
        return 0.0, 0.0

for i in range(cup_len + handle_len, n):
    cup_seg = src[i - cup_len - handle_len:i - handle_len]
    handle_seg = src[i - handle_len:i]

    left_rim = cup_seg[0]
    right_rim = cup_seg[-1]
    cup_low = np.min(cup_seg)
    depth = (min(left_rim, right_rim) - cup_low) / (left_rim + 1e-10) * 100.0

    if depth < depth_pct:
        continue

    rim_diff = abs(left_rim - right_rim) / (left_rim + 1e-10)
    if rim_diff > 0.03:
        continue

    r2, curvature = fit_score(cup_seg)
    if r2 < 0.5 or curvature <= 0:
        continue

    handle_high = np.max(handle_seg)
    handle_low = np.min(handle_seg)
    handle_depth = (handle_high - handle_low) / (handle_high + 1e-10) * 100.0

    if handle_depth > depth * 0.5:
        continue

    if handle_low < cup_low:
        continue

    cup_signal[i] = True
    cup_top[i] = max(left_rim, right_rim)
    cup_bot[i] = cup_low

    if src[i] > handle_high:
        handle_signal[i] = True

for i in range(n):
    if cup_signal[i] and not np.isnan(cup_top[i]) and not np.isnan(cup_bot[i]):
        box.new(left=i - cup_len - handle_len, top=cup_top[i],
                right=i, bottom=cup_bot[i],
                border_color="rgba(66,165,245,0.4)", bgcolor="rgba(66,165,245,0.06)")
    if handle_signal[i] and show_labels:
        label.new(x=i, y=src[i] * 1.005, text="C&H",
                  style=label.style_label_down, color="#42A5F5",
                  textcolor="#FFFFFF", size="small")

score = np.where(cup_signal, 1.0, 0.0)
plot(score, title="Cup Score", color="#42A5F5", linewidth=1)
