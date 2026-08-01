from tg_scripting import *
import numpy as np

indicator("Liquidity Heatmap", overlay=True)

swing_len = input.int(10, "Swing Lookback", minval=3, maxval=50)
num_levels = input.int(8, "Number of Levels", minval=3, maxval=20)
zone_width = input.float(0.5, "Zone Width (ATR)", minval=0.1, maxval=2.0, step=0.1)
lookback = input.int(100, "Cluster Lookback", minval=20, maxval=200)
show_labels = input.bool(True, "Show Labels")

atr = ta.atr(high, low, close, 14)
swing_high = ta.highest(high, swing_len)
swing_low = ta.lowest(low, swing_len)
n = len(close)

# Collect swing points as estimated stop-loss clusters
swing_highs = []
swing_lows = []
for i in range(swing_len, n - swing_len):
    if high[i] == max(high[max(0, i - swing_len):i + swing_len + 1]):
        swing_highs.append((i, float(high[i])))
    if low[i] == min(low[max(0, i - swing_len):i + swing_len + 1]):
        swing_lows.append((i, float(low[i])))

# Build heatmap intensity at recent levels
heat_up = np.zeros(n)
heat_down = np.zeros(n)

for i in range(lookback, n):
    cur_atr = float(atr[i]) if not np.isnan(atr[i]) else 1.0
    width = cur_atr * zone_width
    cur_price = float(close[i])

    # Count nearby swing highs (short stop clusters above)
    above_count = 0
    for idx, price in swing_highs:
        if idx >= i - lookback and idx < i:
            if 0 < price - cur_price < width * 3:
                above_count += 1

    # Count nearby swing lows (long stop clusters below)
    below_count = 0
    for idx, price in swing_lows:
        if idx >= i - lookback and idx < i:
            if 0 < cur_price - price < width * 3:
                below_count += 1

    heat_up[i] = above_count
    heat_down[i] = below_count

# Normalize to 0-1
max_up = np.nanmax(heat_up) if np.nanmax(heat_up) > 0 else 1
max_down = np.nanmax(heat_down) if np.nanmax(heat_down) > 0 else 1
heat_up_norm = heat_up / max_up
heat_down_norm = heat_down / max_down

# Highlight high-cluster zones
high_cluster = heat_up_norm > 0.6
low_cluster = heat_down_norm > 0.6

bgcolor(high_cluster, color="rgba(255,23,68,0.06)")
bgcolor(low_cluster, color="rgba(0,230,118,0.06)")

plot(swing_high, title="Resistance Level", color="rgba(255,23,68,0.4)", linewidth=1, style="stepline")
plot(swing_low, title="Support Level", color="rgba(0,230,118,0.4)", linewidth=1, style="stepline")

# Draw boxes at strongest cluster zones
if show_labels:
    last_label = -20
    for i in range(lookback, n):
        if high_cluster[i] and i - last_label > 20:
            label.new(
                x=i, y=float(swing_high[i]),
                text="Liq",
                style=label.style_label_down,
                color="rgba(255,23,68,0.5)",
                textcolor="#ff1744",
                size="tiny"
            )
            last_label = i
        elif low_cluster[i] and i - last_label > 20:
            label.new(
                x=i, y=float(swing_low[i]),
                text="Liq",
                style=label.style_label_up,
                color="rgba(0,230,118,0.5)",
                textcolor="#00e676",
                size="tiny"
            )
            last_label = i

plot(heat_up_norm * float(np.nanmax(high)), title="Upper Heat", display="none")
plot(heat_down_norm * float(np.nanmin(low)), title="Lower Heat", display="none")
