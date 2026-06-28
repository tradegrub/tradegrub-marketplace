from tg_scripting import *

# Inputs
period = input.int(50, "Fractal Period", minval=10, maxval=200)
smooth_base = input.float(0.1, "Base Smoothing Alpha", minval=0.01, maxval=0.5)
band_mult = input.float(2.0, "Band Multiplier", minval=0.5, maxval=5.0)
method = input.int(1, "Method (1=Higuchi, 2=BoxCount)", minval=1, maxval=2)

# --- Fractal Dimension via Higuchi Method ---
def higuchi_fd(series, k_max):
    n = len(series)
    if n < k_max * 2:
        return 1.5
    ks = np.arange(1, k_max + 1)
    lengths = np.zeros(k_max)
    for k in ks:
        seg_lengths = []
        for m in range(1, k + 1):
            indices = np.arange(m - 1, n, k)
            if len(indices) < 2:
                continue
            seg = series[indices]
            diffs = np.abs(np.diff(seg))
            norm = (n - 1) / (k * len(diffs)) * np.sum(diffs)
            seg_lengths.append(norm)
        if seg_lengths:
            lengths[k - 1] = np.nanmean(seg_lengths)
    valid = lengths > 0
    if np.sum(valid) < 2:
        return 1.5
    log_k = np.log(1.0 / ks[valid])
    log_l = np.log(lengths[valid])
    slope, _ = np.polyfit(log_k, log_l, 1)
    return np.clip(slope, 1.0, 2.0)

# --- Fractal Dimension via Box-Counting ---
def box_counting_fd(series, num_scales=8):
    n = len(series)
    if n < 16:
        return 1.5
    s_min, s_max = np.min(series), np.max(series)
    if s_max - s_min < 1e-10:
        return 1.0
    norm = (series - s_min) / (s_max - s_min)
    scales = np.logspace(0, np.log10(n / 4), num_scales, dtype=int)
    scales = np.unique(np.clip(scales, 2, n // 2))
    if len(scales) < 2:
        return 1.5
    counts = np.zeros(len(scales))
    for i, scale in enumerate(scales):
        num_boxes = int(np.ceil(n / scale))
        box_count = 0
        for b in range(num_boxes):
            start = b * scale
            end = min(start + scale, n)
            chunk = norm[start:end]
            if len(chunk) == 0:
                continue
            y_min, y_max = np.min(chunk), np.max(chunk)
            boxes_y = max(1, int(np.ceil((y_max - y_min) * n / scale)))
            box_count += boxes_y
        counts[i] = max(box_count, 1)
    valid = counts > 0
    if np.sum(valid) < 2:
        return 1.5
    log_s = np.log(1.0 / scales[valid].astype(float))
    log_n = np.log(counts[valid])
    slope, _ = np.polyfit(log_s, log_n, 1)
    return np.clip(slope, 1.0, 2.0)

# --- Rolling Fractal Dimension Calculation ---
n = len(close)
fractal_dim = np.full(n, 1.5)
k_max = min(10, period // 4)

for i in range(period, n):
    window = close[i - period:i]
    if method == 1:
        fractal_dim[i] = higuchi_fd(window, k_max)
    else:
        fractal_dim[i] = box_counting_fd(window)

# Fill initial values
fractal_dim[:period] = fractal_dim[period]

# --- Adaptive Alpha from Fractal Dimension ---
# FD near 1.0 = trending -> low alpha (responsive)
# FD near 2.0 = choppy/random -> high alpha (more smoothing)
alpha_range = np.clip((fractal_dim - 1.0), 0.0, 1.0)
adaptive_alpha = smooth_base + (1.0 - smooth_base) * (1.0 - alpha_range)
# Invert: high FD -> more smoothing -> smaller alpha for EMA-like
adaptive_alpha = np.clip(smooth_base / (alpha_range + smooth_base), 0.01, 1.0)

# --- Adaptive Smoother (custom EMA with variable alpha) ---
smoothed = np.zeros(n)
smoothed[0] = close[0]
for i in range(1, n):
    a = adaptive_alpha[i]
    smoothed[i] = a * close[i] + (1.0 - a) * smoothed[i - 1]

# --- Adaptive Volatility Bands ---
deviation = np.zeros(n)
for i in range(period, n):
    window_diff = close[i - period:i] - smoothed[i - period:i]
    deviation[i] = np.sqrt(np.mean(window_diff ** 2))
deviation[:period] = deviation[period]

# Scale bands inversely with fractal dimension (wider in trending, tighter in chop)
band_scale = band_mult * (2.0 - alpha_range)
upper_band = smoothed + deviation * band_scale
lower_band = smoothed - deviation * band_scale

# --- Regime Detection ---
trending = fractal_dim < 1.35
choppy = fractal_dim > 1.65

# --- Plots ---
p_smooth = plot(smoothed, title="Adaptive Smooth", color="#2196F3")
p_upper = plot(upper_band, title="Upper Band", color="rgba(33,150,243,0.3)")
p_lower = plot(lower_band, title="Lower Band", color="rgba(33,150,243,0.3)")
fill(p_upper, p_lower, color="rgba(33,150,243,0.08)")

plot(fractal_dim, title="Fractal Dimension", color="#FF9800")
hline(1.5, title="FD Midline", color="gray")
hline(1.35, title="Trend Threshold", color="green")
hline(1.65, title="Chop Threshold", color="red")

bgcolor(trending, color="rgba(76,175,80,0.08)")
bgcolor(choppy, color="rgba(244,67,54,0.08)")
