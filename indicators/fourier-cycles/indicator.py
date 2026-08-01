from tg_scripting import *
import numpy as np
from scipy.fft import rfft, rfftfreq, irfft

indicator("Fourier Cycle Analysis", overlay=False)

top_n = input.int(3, "Top N Frequencies", minval=1, maxval=10)
min_period = input.int(5, "Min Cycle Period", minval=2, maxval=50)
max_period = input.int(100, "Max Cycle Period", minval=20, maxval=500)
smooth_len = input.int(5, "Strength Smoothing", minval=1, maxval=20)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)
detrended = close - ta.sma(close, max_period)

spectrum = rfft(detrended)
freqs = rfftfreq(n, d=1.0)
magnitudes = np.abs(spectrum)

periods = np.zeros(len(freqs))
valid = freqs > 0
periods[valid] = 1.0 / freqs[valid]

mask = (periods >= min_period) & (periods <= max_period)
filtered_mag = np.zeros(len(magnitudes))
filtered_mag[mask] = magnitudes[mask]

top_indices = np.argsort(filtered_mag)[-top_n:]
dominant_period = np.zeros(n)
if len(top_indices) > 0:
    strongest = top_indices[-1]
    if periods[strongest] > 0:
        dominant_period[:] = periods[strongest]

reconstruct_spectrum = np.zeros(len(spectrum), dtype=complex)
reconstruct_spectrum[top_indices] = spectrum[top_indices]
filtered_price = irfft(reconstruct_spectrum, n=n)

cycle_strength = np.zeros(n)
total_power = np.sum(magnitudes[mask] ** 2) if np.any(mask) else 1.0
top_power = np.sum(magnitudes[top_indices] ** 2)
raw_strength = top_power / total_power * 100 if total_power > 0 else 0.0

window = min(smooth_len * 2, n)
for i in range(n):
    local_start = max(0, i - window)
    local_end = min(n, i + window)
    local_slice = detrended[local_start:local_end]
    if len(local_slice) > min_period * 2:
        local_spec = rfft(local_slice)
        local_freqs = rfftfreq(len(local_slice), d=1.0)
        local_mag = np.abs(local_spec)
        local_periods = np.zeros(len(local_freqs))
        lv = local_freqs > 0
        local_periods[lv] = 1.0 / local_freqs[lv]
        lm = (local_periods >= min_period) & (local_periods <= max_period)
        lt = np.sum(local_mag[lm] ** 2) if np.any(lm) else 1.0
        if lt > 0:
            sorted_local = np.sort(local_mag[lm])
            top_local = np.sum(sorted_local[-min(top_n, len(sorted_local)):] ** 2)
            cycle_strength[i] = top_local / lt * 100
    else:
        cycle_strength[i] = raw_strength

cycle_strength_smooth = ta.sma(cycle_strength, smooth_len)

plot(cycle_strength_smooth, title="Cycle Strength %", color="#42A5F5")
plot(filtered_price * 10 + 50, title="Filtered Cycle (scaled)", color="#FF7043")

strong_level = 60.0
weak_level = 30.0
h_strong = hline(strong_level, title="Strong Cycles", color="rgba(102,187,106,0.5)")
h_weak = hline(weak_level, title="Weak Cycles", color="rgba(239,83,80,0.5)")
hline(50, title="Mid", color="rgba(128,128,128,0.3)")

bgcolor(cycle_strength_smooth > strong_level, color="rgba(102,187,106,0.06)")
bgcolor(cycle_strength_smooth < weak_level, color="rgba(239,83,80,0.06)")

last_strong_idx = -100
last_weak_idx = -100
last_dom_idx = -100
cooldown = 25

for i in range(1, n):
    if show_labels:
        if cycle_strength_smooth[i] > strong_level and cycle_strength_smooth[i - 1] <= strong_level and (i - last_strong_idx) > cooldown:
            last_strong_idx = i
            label.new(x=i, y=float(cycle_strength_smooth[i]),
                      text="Strong\nCycles",
                      style=label.style_label_down, color="rgba(102,187,106,0.2)",
                      textcolor="#66bb6a", size="small")

        if cycle_strength_smooth[i] < weak_level and cycle_strength_smooth[i - 1] >= weak_level and (i - last_weak_idx) > cooldown:
            last_weak_idx = i
            label.new(x=i, y=float(cycle_strength_smooth[i]),
                      text="Weak\nCycles",
                      style=label.style_label_up, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")

    if show_levels and (i - last_dom_idx) > cooldown * 3:
        if i == n - 1 or (i % (cooldown * 3) == 0):
            last_dom_idx = i
            dp = float(dominant_period[i])
            if dp > 0:
                label.new(x=i, y=float(strong_level + 5),
                          text=f"Dom: {dp:.0f} bars",
                          style=label.style_none, color="rgba(0,0,0,0)",
                          textcolor="#90caf9", size="small")
