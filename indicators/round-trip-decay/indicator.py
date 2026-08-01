from tg_scripting import *
import numpy as np

cycle_length = input.int(252, "Cycle Length (bars)", minval=50, maxval=1000)

c = np.array(close, dtype=float)
n = len(c)

# Compute bar-to-bar returns
returns = np.zeros(n)
returns[1:] = (c[:-1] - c[1:]) / c[1:]  # Note: index 0 is most recent

# Build average return at each cycle position
# Position within cycle for each bar
positions = np.arange(n) % cycle_length

# Average return at each position across all complete cycles
avg_returns = np.zeros(cycle_length)
counts = np.zeros(cycle_length)

for i in range(n):
    pos = positions[i]
    avg_returns[pos] += returns[i]
    counts[pos] += 1

# Avoid division by zero
counts = np.maximum(counts, 1)
avg_returns = avg_returns / counts

# Smooth the cycle pattern
kernel_size = max(5, cycle_length // 20)
kernel = np.ones(kernel_size) / kernel_size
avg_returns_smooth = np.convolve(avg_returns, kernel, mode="same")

# Map each bar to its cycle score (cumulative seasonal return)
cumulative = np.cumsum(avg_returns_smooth)
# Normalize to -100 to 100
max_abs = np.max(np.abs(cumulative)) if np.max(np.abs(cumulative)) > 0 else 1
cumulative = cumulative / max_abs * 100.0

# Create output series: each bar gets the score for its cycle position
scores = np.zeros(n)
for i in range(n):
    scores[i] = cumulative[positions[i]]

plot(scores, title="Cycle Projection", color="#AA66FF")
hline(0.0, title="Neutral", color="#666666")
hline(50.0, title="Bullish Zone", color="#00AA55")
hline(-50.0, title="Bearish Zone", color="#FF4444")

bgcolor(scores > 50, color="rgba(0,170,85,0.08)")
bgcolor(scores < -50, color="rgba(255,68,68,0.08)")
