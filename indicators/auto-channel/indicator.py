from tg_scripting import *
import numpy as np

indicator("Auto Channel Detection", overlay=True)

length = input.int(50, "Channel Length", minval=20, maxval=200)
dev_mult = input.float(1.0, "Width Multiplier", minval=0.5, maxval=3.0, step=0.1)
show_mid = input.bool(True, "Show Midline")

try:
    from scipy.stats import linregress
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

src_h = np.array(high, dtype=float)
src_l = np.array(low, dtype=float)
src_c = np.array(close, dtype=float)
n = len(src_c)

upper = np.full(n, np.nan)
lower = np.full(n, np.nan)
middle = np.full(n, np.nan)

def lin_fit(y):
    x = np.arange(len(y), dtype=float)
    if HAS_SCIPY:
        res = linregress(x, y)
        return res.slope, res.intercept
    else:
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        ss_xy = np.sum((x - x_mean) * (y - y_mean))
        ss_xx = np.sum((x - x_mean) ** 2)
        slope = ss_xy / (ss_xx + 1e-10)
        intercept = y_mean - slope * x_mean
        return slope, intercept

for i in range(length, n):
    seg = src_c[i - length:i]
    slope, intercept = lin_fit(seg)

    xs = np.arange(length, dtype=float)
    fitted = slope * xs + intercept
    residuals = seg - fitted

    upper_dev = np.max(residuals) * dev_mult
    lower_dev = np.min(residuals) * dev_mult

    mid_val = slope * (length - 1) + intercept
    middle[i] = mid_val
    upper[i] = mid_val + upper_dev
    lower[i] = mid_val + lower_dev

    if i == n - 1:
        start = i - length
        mid_start = intercept
        line.new(x1=start, y1=mid_start + upper_dev, x2=i, y2=mid_val + upper_dev,
                 color="#42A5F5", width=1, style=line.style_solid)
        line.new(x1=start, y1=mid_start + lower_dev, x2=i, y2=mid_val + lower_dev,
                 color="#42A5F5", width=1, style=line.style_solid)
        if show_mid:
            line.new(x1=start, y1=mid_start, x2=i, y2=mid_val,
                     color="#42A5F5", width=1, style=line.style_dashed)
        box.new(left=start, top=mid_start + upper_dev, right=i,
                bottom=mid_start + lower_dev,
                border_color="rgba(66,165,245,0.0)", bgcolor="rgba(66,165,245,0.04)")

plot(upper, title="Upper Channel", color="#42A5F5", linewidth=1)
plot(lower, title="Lower Channel", color="#42A5F5", linewidth=1)
if show_mid:
    plot(middle, title="Midline", color="rgba(66,165,245,0.4)", linewidth=1)
