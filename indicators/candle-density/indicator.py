from tg_scripting import *
import numpy as np

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
num_bins = input.int(30, "Number of Bins", minval=10, maxval=100)

# Get OHLC data for lookback period
o = np.array(open[:lookback], dtype=float)
c = np.array(close[:lookback], dtype=float)
h = np.array(high[:lookback], dtype=float)
l = np.array(low[:lookback], dtype=float)

# Candle body boundaries
body_top = np.maximum(o, c)
body_bot = np.minimum(o, c)

# Price range for binning
price_min = np.min(l)
price_max = np.max(h)
bin_edges = np.linspace(price_min, price_max, num_bins + 1)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

# Count how many candle bodies overlap each bin
density = np.zeros(num_bins)
for i in range(len(o)):
    mask = (bin_centers >= body_bot[i]) & (bin_centers <= body_top[i])
    density[mask] += 1.0

# Normalize to 0-100
max_density = np.max(density)
if max_density > 0:
    density = density / max_density * 100.0

# Current bar's density score: average density of bins overlapping current bar's body
cur_top = float(max(open[0], close[0]))
cur_bot = float(min(open[0], close[0]))
cur_mask = (bin_centers >= cur_bot) & (bin_centers <= cur_top)
if np.any(cur_mask):
    score = np.mean(density[cur_mask])
else:
    score = 0.0

# Build a series of density scores for plotting
scores = np.full(len(close), np.nan)
scores[0] = score

# Compute for recent bars too
for bar in range(1, min(lookback, len(close))):
    bt = float(max(open[bar], close[bar]))
    bb = float(min(open[bar], close[bar]))
    m = (bin_centers >= bb) & (bin_centers <= bt)
    if np.any(m):
        scores[bar] = float(np.mean(density[m]))
    else:
        scores[bar] = 0.0

plot(scores, title="Candle Density", color="#FF9900")
hline(75.0, title="High Congestion", color="#FF4444")
hline(25.0, title="Low Congestion", color="#00AA55")

bgcolor(scores > 75, color="rgba(255,68,68,0.1)")
