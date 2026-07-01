from tg_scripting import *
import numpy as np

indicator("Volume Footprint Imbalance", overlay=False)

num_levels = input.int(5, "Price Levels", minval=3, maxval=10)
imbalance_threshold = input.float(2.0, "Imbalance Threshold", minval=1.5, maxval=5.0, step=0.1)
smoothing = input.int(3, "Smoothing", minval=1, maxval=10)

n = len(close)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
op = np.array(open, dtype=float)
cl = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)

net_imbalance = np.zeros(n)
stacked_signal = np.zeros(n)

for i in range(n):
    bar_range = hi[i] - lo[i]
    if bar_range <= 0 or vol[i] <= 0:
        continue

    body_top = max(op[i], cl[i])
    body_bot = min(op[i], cl[i])
    upper_wick = hi[i] - body_top
    lower_wick = body_bot - lo[i]
    is_bullish = cl[i] >= op[i]
    close_pos = (cl[i] - lo[i]) / bar_range

    zone_size = bar_range / num_levels
    total_buy = 0.0
    total_sell = 0.0
    stacked_count = 0
    prev_imbalanced = False

    for z in range(num_levels):
        zone_mid = lo[i] + (z + 0.5) * zone_size
        zone_high = lo[i] + (z + 1) * zone_size
        zone_vol = vol[i] / num_levels
        zone_pos = (zone_mid - lo[i]) / bar_range
        proximity = max(0.1, 1.0 - abs(zone_pos - close_pos))

        sell_bias = 0.5
        if zone_high > body_top and upper_wick > 0:
            sell_bias = 0.6 + 0.2 * min(1.0, (zone_mid - body_top) / upper_wick)
        elif zone_mid < body_bot and lower_wick > 0:
            sell_bias = 0.4 - 0.2 * min(1.0, (body_bot - zone_mid) / lower_wick)
        elif is_bullish:
            sell_bias = 0.35 - 0.1 * proximity
        else:
            sell_bias = 0.65 + 0.1 * proximity

        sell_bias = np.clip(sell_bias, 0.1, 0.9)
        buy_vol = max(0.01, zone_vol * (1 - sell_bias) * (0.5 + proximity))
        sell_vol = max(0.01, zone_vol * sell_bias * (0.5 + (1 - proximity)))

        total_buy += buy_vol
        total_sell += sell_vol

        ratio = buy_vol / sell_vol
        inv_ratio = sell_vol / buy_vol
        level_imbalanced = ratio > imbalance_threshold or inv_ratio > imbalance_threshold

        if level_imbalanced and prev_imbalanced:
            stacked_count += 1
        prev_imbalanced = level_imbalanced

    if total_sell > 0:
        net_imbalance[i] = (total_buy - total_sell) / (total_buy + total_sell)
    stacked_signal[i] = stacked_count

smoothed = np.copy(net_imbalance)
if smoothing > 1:
    alpha = 2.0 / (smoothing + 1)
    for i in range(1, n):
        smoothed[i] = alpha * net_imbalance[i] + (1 - alpha) * smoothed[i - 1]

plot(smoothed.tolist(), title="Net Imbalance", color="#FFD700", linewidth=2)
plot(net_imbalance.tolist(), title="Imbalance", color="#78909C", style=plot.style_histogram)
plot((stacked_signal / num_levels).tolist(), title="Stacked", color="#FF6D00", linewidth=1)

hline(0, title="Zero", color="#555555", linestyle="dashed")
hline(0.3, title="Buy Zone", color="#4CAF50", linestyle="dotted")
hline(-0.3, title="Sell Zone", color="#EF5350", linestyle="dotted")
