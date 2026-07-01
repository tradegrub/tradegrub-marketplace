from tg_scripting import *
import numpy as np

indicator("Wavelet Multi-Resolution Analysis", overlay=False)

levels = input.int(3, "Decomposition Levels", minval=1, maxval=5)
show_approx = input.bool(True, "Show Approximation")

src = np.array(close, dtype=float)
n = len(src)

# Haar wavelet transform (no scipy dependency needed)
def haar_decompose(signal, max_level):
    details = []
    approx = signal.copy()
    for level in range(max_level):
        length = len(approx)
        if length < 4:
            break
        half = length // 2 * 2  # make even
        a = approx[:half]
        new_approx = np.zeros(half // 2)
        detail = np.zeros(half // 2)
        for i in range(half // 2):
            new_approx[i] = (a[2 * i] + a[2 * i + 1]) / np.sqrt(2)
            detail[i] = (a[2 * i] - a[2 * i + 1]) / np.sqrt(2)
        # Upsample detail back to original length
        detail_full = np.zeros(n)
        scale = n / len(detail)
        for j in range(len(detail)):
            idx_start = int(j * scale)
            idx_end = int((j + 1) * scale)
            detail_full[idx_start:idx_end] = detail[j]
        details.append(detail_full)
        approx = new_approx
    # Upsample approximation
    approx_full = np.zeros(n)
    scale = n / len(approx)
    for j in range(len(approx)):
        idx_start = int(j * scale)
        idx_end = int((j + 1) * scale)
        approx_full[idx_start:idx_end] = approx[j]
    return details, approx_full


# Demean for better visualization
src_dm = src - np.mean(src)
details, approx = haar_decompose(src_dm, levels)

# Normalize each detail level
colors = ["#42A5F5", "#AB47BC", "#FFA726", "#4CAF50", "#EF5350"]
for i, detail in enumerate(details):
    std = np.std(detail)
    if std > 0:
        norm = (detail / std) * 15
    else:
        norm = detail
    offset = (i - len(details) // 2) * 35
    plot((norm + offset).tolist(), title=f"Detail D{i + 1}", color=colors[i % len(colors)], linewidth=1)

if show_approx and len(details) > 0:
    std_a = np.std(approx)
    if std_a > 0:
        approx_norm = (approx / std_a) * 15
    else:
        approx_norm = approx
    offset_a = (len(details) - len(details) // 2) * 35
    plot((approx_norm + offset_a).tolist(), title="Approx A", color="#FFFFFF", linewidth=2)

hline(0, title="Zero", color="#444", linestyle="dashed")
