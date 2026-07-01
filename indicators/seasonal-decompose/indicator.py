from tg_scripting import *
import numpy as np

indicator("Seasonal Decomposition", overlay=False)

trend_len = input.int(20, "Trend Length", minval=5, maxval=100)
season_len = input.int(10, "Seasonal Period", minval=3, maxval=50)
fft_components = input.int(3, "FFT Components", minval=1, maxval=10)
smooth_residual = input.int(5, "Residual Smoothing", minval=1, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

close_arr = np.array(close, dtype=np.float64)
n = len(close_arr)

# Trend: rolling mean (pandas-style)
trend = np.array(ta.sma(close, trend_len), dtype=np.float64)
for i in range(trend_len):
    trend[i] = close_arr[i]

# Detrended
detrended = close_arr - trend

# Seasonal: FFT-based extraction on detrended data
spectrum = np.fft.rfft(detrended)
freqs = np.fft.rfftfreq(n, d=1.0)
magnitudes = np.abs(spectrum)

# Keep only seasonal-frequency components
periods = np.zeros(len(freqs))
valid_f = freqs > 0
periods[valid_f] = 1.0 / freqs[valid_f]

seasonal_mask = (periods >= season_len * 0.5) & (periods <= season_len * 3.0)
filtered_mag = np.zeros(len(magnitudes))
filtered_mag[seasonal_mask] = magnitudes[seasonal_mask]

top_indices = np.argsort(filtered_mag)[-fft_components:]
seasonal_spectrum = np.zeros(len(spectrum), dtype=complex)
seasonal_spectrum[top_indices] = spectrum[top_indices]
seasonal = np.fft.irfft(seasonal_spectrum, n=n)

# Residual
residual = detrended - seasonal

# Normalize for display
def normalize(arr, center=50, scale=20):
    arr_clean = arr[np.isfinite(arr)]
    if len(arr_clean) == 0:
        return np.full(len(arr), center)
    mn, mx = arr_clean.min(), arr_clean.max()
    rng = mx - mn
    if rng < 1e-10:
        return np.full(len(arr), center)
    return (arr - mn) / rng * scale * 2 + (center - scale)

trend_norm = normalize(trend, 80, 15)
seasonal_norm = normalize(seasonal, 50, 15)
residual_smooth = np.array(ta.sma(residual, smooth_residual), dtype=np.float64)
for i in range(smooth_residual):
    residual_smooth[i] = residual[i]
residual_norm = normalize(residual_smooth, 20, 15)

plot(trend_norm, title="Trend", color="#42A5F5")
plot(seasonal_norm, title="Seasonal", color="#FF9800")
plot(residual_norm, title="Residual", color="#AB47BC")

hline(80, title="Trend Center", color="rgba(66,165,245,0.2)")
hline(50, title="Seasonal Center", color="rgba(255,152,0,0.2)")
hline(20, title="Residual Center", color="rgba(171,71,188,0.2)")

# Trend direction coloring
trend_rising = np.zeros(n, dtype=bool)
trend_falling = np.zeros(n, dtype=bool)
for i in range(1, n):
    if trend[i] > trend[i - 1]:
        trend_rising[i] = True
    elif trend[i] < trend[i - 1]:
        trend_falling[i] = True


if show_labels:
    last_peak_idx = -30
    last_trough_idx = -30
    cooldown = 20
    for i in range(2, n - 1):
        if seasonal[i] > seasonal[i - 1] and seasonal[i] > seasonal[i + 1] and (i - last_peak_idx) > cooldown:
            last_peak_idx = i
            label.new(x=i, y=float(seasonal_norm[i]),
                      text="Seasonal\nPeak",
                      style=label.style_label_down, color="rgba(255,152,0,0.2)",
                      textcolor="#FF9800", size="small")
        if seasonal[i] < seasonal[i - 1] and seasonal[i] < seasonal[i + 1] and (i - last_trough_idx) > cooldown:
            last_trough_idx = i
            label.new(x=i, y=float(seasonal_norm[i]),
                      text="Seasonal\nTrough",
                      style=label.style_label_up, color="rgba(255,152,0,0.2)",
                      textcolor="#FF9800", size="small")

if show_levels:
    # Dominant seasonal period
    strongest = top_indices[-1] if len(top_indices) > 0 else 0
    dom_period = periods[strongest] if strongest < len(periods) and periods[strongest] > 0 else 0

    # Residual volatility
    res_std = np.std(residual[np.isfinite(residual)])
    trend_pct = np.std(trend[np.isfinite(trend)]) / np.mean(np.abs(close_arr)) * 100

    label.new(x=n - 1, y=95.0,
              text=f"Period: {dom_period:.0f} bars\nResidual SD: {res_std:.2f}\nTrend Vol: {trend_pct:.1f}%",
              style=label.style_label_left, color="rgba(66,165,245,0.15)",
              textcolor="#90caf9", size="small")
