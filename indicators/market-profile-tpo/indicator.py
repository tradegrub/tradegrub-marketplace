from tg_scripting import *
import numpy as np

indicator("Market Profile TPO", overlay=True)

num_bins = input.int(30, "Number of Bins", minval=10, maxval=100)
lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
value_area_pct = input.int(70, "Value Area %", minval=50, maxval=90)
show_poc = input.bool(True, "Show POC")
show_value_area = input.bool(True, "Show Value Area")

n = len(close)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)

lb = min(lookback, n)
h = hi[-lb:]
l = lo[-lb:]

range_high = np.max(h)
range_low = np.min(l)
price_range = range_high - range_low

if price_range > 0 and lb >= 2:
    bin_size = price_range / num_bins
    tpo_counts = np.zeros(num_bins, dtype=int)

    for i in range(lb):
        bar_low = l[i]
        bar_high = h[i]
        first_bin = int((bar_low - range_low) / bin_size)
        last_bin = int((bar_high - range_low) / bin_size)
        first_bin = max(0, min(first_bin, num_bins - 1))
        last_bin = max(0, min(last_bin, num_bins - 1))
        tpo_counts[first_bin:last_bin + 1] += 1

    poc_idx = int(np.argmax(tpo_counts))
    poc_price = range_low + (poc_idx + 0.5) * bin_size

    total_tpo = int(np.sum(tpo_counts))
    target_tpo = total_tpo * value_area_pct / 100.0
    va_low_idx = poc_idx
    va_high_idx = poc_idx
    accumulated = int(tpo_counts[poc_idx])

    while accumulated < target_tpo:
        expand_up = tpo_counts[va_high_idx + 1] if va_high_idx + 1 < num_bins else -1
        expand_down = tpo_counts[va_low_idx - 1] if va_low_idx - 1 >= 0 else -1
        if expand_up < 0 and expand_down < 0:
            break
        if expand_up >= expand_down:
            va_high_idx += 1
            accumulated += int(tpo_counts[va_high_idx])
        else:
            va_low_idx -= 1
            accumulated += int(tpo_counts[va_low_idx])

    vah_price = range_low + (va_high_idx + 1) * bin_size
    val_price = range_low + va_low_idx * bin_size

    poc_arr = np.full(n, poc_price)
    vah_arr = np.full(n, vah_price)
    val_arr = np.full(n, val_price)

    if show_poc:
        plot(poc_arr.tolist(), title="POC", color="#FFD700", linewidth=2)

    if show_value_area:
        p_vah = plot(vah_arr.tolist(), title="VAH", color="#4CAF50", linewidth=1)
        p_val = plot(val_arr.tolist(), title="VAL", color="#EF5350", linewidth=1)
        fill(p_vah, p_val, color="rgba(33,150,243,0.1)")
