from tg_scripting import *
import numpy as np

indicator("Signal to Noise Ratio", overlay=False)

length = input.int(14, "Length", minval=5, maxval=100)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)
signal_thresh = input.float(1.5, "Strong Signal Threshold", minval=0.5, maxval=5.0, step=0.1)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

# Signal: directional movement over the window
signal_arr = np.zeros(n)
noise_arr = np.zeros(n)
snr = np.zeros(n)

for i in range(length, n):
    window_close = src[i - length:i + 1]
    window_high = hi[i - length:i + 1]
    window_low = lo[i - length:i + 1]

    # Signal = net directional movement
    net_move = abs(window_close[-1] - window_close[0])

    # Noise = sum of bar ranges (total movement)
    total_move = 0.0
    for j in range(len(window_high)):
        total_move += window_high[j] - window_low[j]

    signal_arr[i] = net_move
    noise_arr[i] = total_move

    if total_move > 0:
        snr[i] = net_move / total_move * 10  # Scale for readability
    else:
        snr[i] = 0

# Smooth SNR
if smooth > 1:
    kern = np.ones(smooth) / smooth
    snr = np.convolve(snr, kern, mode='same')

# Efficiency ratio (similar concept, 0-100)
efficiency = np.zeros(n)
for i in range(length, n):
    net = abs(src[i] - src[i - length])
    path = 0.0
    for j in range(i - length + 1, i + 1):
        path += abs(src[j] - src[j - 1])
    if path > 0:
        efficiency[i] = (net / path) * 100

if smooth > 1:
    efficiency = np.convolve(efficiency, kern, mode='same')

# Strong signal detection
strong = np.array([snr[i] > signal_thresh for i in range(n)])

plot(snr.tolist(), title="SNR", color="#42A5F5", linewidth=2)
plot(efficiency.tolist(), title="Efficiency Ratio", color="#AB47BC", linewidth=1)
hline(signal_thresh, title="Strong Signal", color="#4CAF50", linestyle="dashed")
hline(0.5, title="Weak Signal", color="#EF5350", linestyle="dashed")
bgcolor(strong, color="rgba(76,175,80,0.06)")
