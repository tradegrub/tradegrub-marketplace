from tg_scripting import *
import numpy as np
from scipy.signal import butter, filtfilt, sosfilt

indicator("Wavelet Denoise Filter", overlay=False)

cutoff_period = input.int(20, "Cutoff Period (bars)", minval=5, maxval=100)
filter_order = input.int(3, "Filter Order", minval=1, maxval=6)
snr_len = input.int(14, "SNR Lookback", minval=5, maxval=50)
smooth_noise = input.int(5, "Noise Smoothing", minval=1, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

close_arr = np.array(close, dtype=np.float64)
n = len(close_arr)

# Butterworth low-pass filter for trend extraction
nyquist = 0.5
cutoff_freq = 1.0 / cutoff_period / nyquist

# Clamp cutoff to valid range
cutoff_freq = min(cutoff_freq, 0.99)
cutoff_freq = max(cutoff_freq, 0.01)

sos = butter(filter_order, cutoff_freq, btype='low', output='sos')

# Pad signal to reduce edge effects
pad_len = min(3 * cutoff_period, n // 2)
padded = np.concatenate([
    close_arr[pad_len:0:-1],
    close_arr,
    close_arr[-2:-pad_len - 2:-1]
])

filtered_padded = sosfilt(sos, padded)
denoised = filtered_padded[pad_len:pad_len + n]

# Noise component
noise = close_arr - denoised

# Signal-to-noise ratio
snr = np.zeros(n)
for i in range(snr_len, n):
    signal_power = np.var(denoised[i - snr_len:i])
    noise_power = np.var(noise[i - snr_len:i])
    if noise_power > 1e-10:
        snr[i] = 10 * np.log10(signal_power / noise_power)
    else:
        snr[i] = 30.0

# Normalize for display
price_range = close_arr.max() - close_arr.min()
if price_range < 1e-10:
    price_range = 1.0

# Denoised trend normalized to 0-100
denoised_norm = (denoised - close_arr.min()) / price_range * 60 + 20
original_norm = (close_arr - close_arr.min()) / price_range * 60 + 20

# Noise normalized around 50
noise_smooth = np.array(ta.sma(np.abs(noise), smooth_noise), dtype=np.float64)
for i in range(smooth_noise):
    noise_smooth[i] = abs(noise[i])
noise_max = noise_smooth.max() if noise_smooth.max() > 1e-10 else 1.0
noise_norm = noise_smooth / noise_max * 30 + 5

plot(original_norm, title="Original Price", color="rgba(255,255,255,0.3)")
plot(denoised_norm, title="Denoised Trend", color="#42A5F5")
plot(noise_norm, title="Noise Level", color="#FF7043")

hline(50, title="Mid", color="rgba(128,128,128,0.2)")

# SNR sub-indicator via bgcolor
high_snr = snr > 10
low_snr = snr < 3

bgcolor(high_snr, color="rgba(102,187,106,0.05)")
bgcolor(low_snr, color="rgba(239,83,80,0.05)")

# Trend direction from denoised
trend_up = np.zeros(n, dtype=bool)
trend_down = np.zeros(n, dtype=bool)
for i in range(1, n):
    if denoised[i] > denoised[i - 1]:
        trend_up[i] = True
    elif denoised[i] < denoised[i - 1]:
        trend_down[i] = True

if show_labels:
    last_up_idx = -30
    last_down_idx = -30
    cooldown = 25
    prev_dir = 0
    for i in range(2, n):
        curr_dir = 1 if trend_up[i] else (-1 if trend_down[i] else 0)
        if curr_dir == 1 and prev_dir <= 0 and (i - last_up_idx) > cooldown:
            last_up_idx = i
            label.new(x=i, y=float(denoised_norm[i]),
                      text="Trend\nUp",
                      style=label.style_label_up, color="rgba(102,187,106,0.2)",
                      textcolor="#66bb6a", size="small")
        elif curr_dir == -1 and prev_dir >= 0 and (i - last_down_idx) > cooldown:
            last_down_idx = i
            label.new(x=i, y=float(denoised_norm[i]),
                      text="Trend\nDown",
                      style=label.style_label_down, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
        if curr_dir != 0:
            prev_dir = curr_dir

if show_levels:
    avg_snr = np.mean(snr[snr_len:])
    avg_noise = np.mean(noise_smooth)
    noise_pct = avg_noise / np.mean(close_arr) * 100
    label.new(x=n - 1, y=90.0,
              text=f"SNR: {avg_snr:.1f} dB\nNoise: {noise_pct:.2f}%\nCutoff: {cutoff_period} bars",
              style=label.style_label_left, color="rgba(66,165,245,0.15)",
              textcolor="#90caf9", size="small")
