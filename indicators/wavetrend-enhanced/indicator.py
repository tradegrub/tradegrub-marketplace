from tg_scripting import *
import numpy as np

channel_length = input.int(10, "Channel Length", minval=1, maxval=50)
average_length = input.int(21, "Average Length", minval=1, maxval=50)

src = close


def ema_np(source, length):
    """Compute EMA manually with numpy."""
    alpha = 2.0 / (length + 1)
    result = np.empty_like(source, dtype=float)
    result[0] = source[0]
    for i in range(1, len(source)):
        result[i] = alpha * source[i] + (1 - alpha) * result[i - 1]
    return result


def sma_np(source, length):
    """Compute SMA with numpy."""
    result = np.empty_like(source, dtype=float)
    cumsum = np.cumsum(source)
    result[:length] = cumsum[:length] / np.arange(1, length + 1)
    result[length:] = (cumsum[length:] - cumsum[:-length]) / length
    return result


# Channel index calculation
ema_src = ema_np(src, channel_length)
diff = np.abs(src - ema_src)
ema_diff = ema_np(diff, channel_length)
ci = (src - ema_src) / (0.015 * ema_diff + 1e-10)

# Double EMA smoothing
wt1 = ema_np(ci, average_length)
wt2 = sma_np(wt1, 4)

# Divergence detection: find local minima in price and wt1
def find_local_minima(arr, order=5):
    """Find local minima indices using numpy comparisons."""
    minima = np.zeros(len(arr), dtype=bool)
    for i in range(order, len(arr) - order):
        is_min = True
        for j in range(1, order + 1):
            if arr[i] > arr[i - j] or arr[i] > arr[i + j]:
                is_min = False
                break
        if is_min:
            minima[i] = True
    return minima


price_minima = find_local_minima(src, order=5)
wt1_minima = find_local_minima(wt1, order=5)

# Bullish divergence: price makes lower low but wt1 makes higher low
bull_div = np.zeros(len(src), dtype=bool)
price_min_indices = np.where(price_minima)[0]
wt1_min_indices = np.where(wt1_minima)[0]

for i in range(1, len(price_min_indices)):
    curr_idx = price_min_indices[i]
    prev_idx = price_min_indices[i - 1]
    # Price lower low
    if src[curr_idx] < src[prev_idx]:
        # Find nearest wt1 minimum near current and previous price minima
        wt1_near_curr = wt1_min_indices[np.abs(wt1_min_indices - curr_idx) <= 5]
        wt1_near_prev = wt1_min_indices[np.abs(wt1_min_indices - prev_idx) <= 5]
        if len(wt1_near_curr) > 0 and len(wt1_near_prev) > 0:
            wt1_curr_val = wt1[wt1_near_curr[0]]
            wt1_prev_val = wt1[wt1_near_prev[0]]
            # wt1 higher low = bullish divergence
            if wt1_curr_val > wt1_prev_val:
                bull_div[curr_idx] = True

# Plotting
plot(wt1, title="WT1", color="#26C6DA")
plot(wt2, title="WT2", color="#FF9800")

hline(60, title="Overbought", color="#EF5350")
hline(-60, title="Oversold", color="#4CAF50")
hline(0, title="Zero", color="#888888")

plotshape(bull_div, title="Bullish Divergence", style="triangleup",
          location="belowbar", color="#4CAF50")
