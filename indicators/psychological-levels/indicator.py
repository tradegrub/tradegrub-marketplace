from tg_scripting import *
import numpy as np

# Get current price to determine scale
price = float(close[0])

# Determine interval based on price magnitude
if price < 10:
    interval = 0.5
elif price < 100:
    interval = 5.0
elif price < 1000:
    interval = 25.0
else:
    interval = 100.0

# Compute round number levels around current price
# Show levels within +/- 10 intervals of current price
base = np.floor(price / interval) * interval
levels = np.arange(base - 10 * interval, base + 11 * interval, interval)

# Filter to reasonable range around price (within 20% band)
band = price * 0.2
levels = levels[(levels >= price - band) & (levels <= price + band)]

# Draw up to 15 horizontal lines at round number levels
colors = ["#5555FF", "#FF5555", "#55AA55", "#FFAA00", "#AA55FF",
          "#55AAAA", "#FF55AA", "#AAAA55", "#5599FF", "#FF9955",
          "#99FF55", "#FF5599", "#55FF99", "#9955FF", "#FFFF55"]

for i, level in enumerate(levels[:15]):
    hline(float(level), title=f"Level {float(level):.2f}", color=colors[i % len(colors)])
