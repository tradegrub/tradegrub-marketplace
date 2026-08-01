from tg_scripting import *
import numpy as np

indicator("Hilbert Transform Trendline", overlay=True)

length = input.int(20, "Smoothing Length", minval=5, maxval=100)
src_smooth = input.int(5, "Source Smoothing", minval=1, maxval=20)

try:
    from scipy.signal import hilbert
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

src = np.array(close, dtype=float)

# Smooth source
if src_smooth > 1:
    kernel = np.ones(src_smooth) / src_smooth
    src = np.convolve(src, kernel, mode='same')

# Detrend using simple moving average
trend = ta.sma(src.tolist(), length)
detrended = src - np.array(trend, dtype=float)
detrended = np.nan_to_num(detrended, nan=0.0)

if HAS_SCIPY:
    analytic = hilbert(detrended)
    inst_phase = np.angle(analytic)
    amplitude = np.abs(analytic)
else:
    # Manual Hilbert-like via finite differences
    inst_phase = np.zeros(len(detrended))
    amplitude = np.abs(detrended)
    for i in range(1, len(detrended)):
        if amplitude[i] > 0:
            inst_phase[i] = np.arctan2(detrended[i - 1], detrended[i])

# Compute instantaneous frequency (dominant period)
phase_diff = np.diff(inst_phase, prepend=inst_phase[0])
# Unwrap phase differences to [-pi, pi]
phase_diff = (phase_diff + np.pi) % (2 * np.pi) - np.pi
# Avoid division by zero
phase_diff = np.where(np.abs(phase_diff) < 0.01, 0.01, phase_diff)
dominant_period = 2 * np.pi / np.abs(phase_diff)
dominant_period = np.clip(dominant_period, 2, 100)

# Smooth outputs
kern = np.ones(5) / 5
dominant_period = np.convolve(dominant_period, kern, mode='same')
amplitude_smooth = np.convolve(amplitude, kern, mode='same')

# Normalize amplitude for plotting
amp_max = np.nanmax(amplitude_smooth)
if amp_max > 0:
    amplitude_norm = (amplitude_smooth / amp_max) * 50

# Phase normalized to 0-100
phase_norm = ((inst_phase + np.pi) / (2 * np.pi)) * 100

plot(dominant_period.tolist(), title="Dominant Period", color="#42A5F5", linewidth=2)
plot(phase_norm.tolist(), title="Phase (0-100)", color="#AB47BC", linewidth=1)
hline(20, title="Fast Cycle", color="#4CAF50", linestyle="dashed")
hline(50, title="Medium Cycle", color="#FFA726", linestyle="dashed")
