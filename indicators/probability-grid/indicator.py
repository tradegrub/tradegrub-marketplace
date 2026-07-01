from tg_scripting import *
import numpy as np

indicator("Probability Reversal Grid", overlay=False)

lookback = input.int(100, "Lookback", minval=20, maxval=500)
num_zones = input.int(10, "Number of Zones", minval=5, maxval=50)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

reversal_prob = np.full(n, 50.0)

if n > lookback + 2:
    for i in range(lookback + 2, n):
        seg = src[i - lookback:i]
        seg_min = float(np.min(seg))
        seg_max = float(np.max(seg))
        seg_range = seg_max - seg_min

        if seg_range < 0.001:
            continue

        position = (seg - seg_min) / seg_range * 100.0
        zone_edges = np.linspace(0, 100, num_zones + 1)

        current_pos = float(position[-1])
        current_zone = int(np.digitize(current_pos, zone_edges)) - 1
        current_zone = max(0, min(current_zone, num_zones - 1))

        zone_low = zone_edges[current_zone]
        zone_high = zone_edges[min(current_zone + 1, num_zones)]

        in_zone = (position[:-2] >= zone_low) & (position[:-2] <= zone_high)
        zone_indices = np.where(in_zone)[0]

        if len(zone_indices) > 3:
            next_moves = src[i - lookback + zone_indices + 1] - src[i - lookback + zone_indices]
            next_next = src[i - lookback + zone_indices + 2] - src[i - lookback + zone_indices + 1]

            direction = np.sign(next_moves)
            reversal = np.sign(next_next) != direction
            reversal_prob[i] = float(np.sum(reversal)) / float(len(reversal)) * 100.0

plot(reversal_prob.tolist(), title="Reversal Probability", color="#E91E63", linewidth=2)
hline(70, title="High Reversal Zone", color="#FF9800", linestyle="dashed")
hline(50, title="Neutral", color="#555555", linestyle="dashed")

high_prob = reversal_prob > 70
bgcolor(high_prob.tolist(), color="rgba(233,30,99,0.08)")
