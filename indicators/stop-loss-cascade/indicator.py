from tg_scripting import *
import numpy as np

swing_lookback = input.int(20, "Swing Lookback", minval=5, maxval=100)
cluster_atr_mult = input.float(0.5, "Cluster ATR Mult", minval=0.1, maxval=3.0)

atr_val = ta.atr(high, low, close, 14)
current_atr = float(atr_val[0])
cluster_threshold = current_atr * float(cluster_atr_mult)

lookback = int(swing_lookback)
high_arr = np.array(high[:lookback], dtype=float)
low_arr = np.array(low[:lookback], dtype=float)
close_arr = np.array(close[:lookback], dtype=float)
current_close = float(close[0])

# Find swing highs and lows using numpy
swing_highs = []
swing_lows = []
margin = 2
for i in range(margin, len(high_arr) - margin):
    if high_arr[i] == np.max(high_arr[i - margin:i + margin + 1]):
        swing_highs.append(high_arr[i])
    if low_arr[i] == np.min(low_arr[i - margin:i + margin + 1]):
        swing_lows.append(low_arr[i])

all_swings = np.array(swing_highs + swing_lows)

# Count cascade clusters: how many swing levels within threshold of each other
cascade_intensity = np.zeros(len(close))
proximity = np.zeros(len(close))

if len(all_swings) > 1:
    all_swings_sorted = np.sort(all_swings)
    # For each swing, count neighbors within cluster_threshold
    max_cluster = 0
    for s in all_swings_sorted:
        neighbors = np.sum(np.abs(all_swings_sorted - s) <= cluster_threshold)
        if neighbors > max_cluster:
            max_cluster = neighbors
    # Normalize to 0-100
    raw_intensity = (max_cluster / max(len(all_swings), 1)) * 100
    # Proximity: how close is price to any cluster zone
    min_dist = np.min(np.abs(all_swings - current_close))
    prox = max(0, 1 - min_dist / (current_atr * 2)) * 100

    for i in range(len(close)):
        c = float(close[i])
        dist = np.min(np.abs(all_swings - c))
        p = max(0, 1 - dist / (current_atr * 2)) * 100
        cascade_intensity[i] = raw_intensity * (p / 100)
        proximity[i] = p

plot(cascade_intensity, title="Cascade Intensity", color=color.red)
plot(proximity, title="Proximity", color=color.gray)
hline(70, title="High Cascade", color=color.orange)
hline(30, title="Low Cascade", color=color.green)
bgcolor(cascade_intensity > 70, color="rgba(255,0,0,0.1)")
