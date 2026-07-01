from tg_scripting import *
import numpy as np

length = input.int(14, "Length", minval=2, maxval=100)

# Manual ROC: percent change over 'length' bars
price_roc = np.full_like(close, np.nan, dtype=float)
vol_roc = np.full_like(close, np.nan, dtype=float)

for i in range(length, len(close)):
    if close[i - length] != 0:
        price_roc[i] = (close[i] - close[i - length]) / close[i - length]
    if volume[i - length] != 0:
        vol_roc[i] = (volume[i] - volume[i - length]) / volume[i - length]

# Normalize to -1..1 using clip after scaling by rolling max absolute value
def normalize(arr, win):
    out = np.full_like(arr, np.nan, dtype=float)
    for i in range(win, len(arr)):
        window = arr[max(0, i - win + 1):i + 1]
        valid = window[~np.isnan(window)]
        if len(valid) > 0:
            mx = np.max(np.abs(valid))
            if mx > 0:
                out[i] = np.clip(arr[i] / mx, -1.0, 1.0)
            else:
                out[i] = 0.0
    return out

norm_price = normalize(price_roc, length * 2)
norm_vol = normalize(vol_roc, length * 2)

# Quadrant detection
q1 = (norm_price > 0) & (norm_vol > 0)   # Accumulation
q2 = (norm_price > 0) & (norm_vol <= 0)  # Distribution warning
q3 = (norm_price <= 0) & (norm_vol <= 0) # Distribution
q4 = (norm_price <= 0) & (norm_vol > 0)  # Panic / accumulation start

# Background coloring by quadrant
bgcolor(q1, color="rgba(0,200,100,0.15)")
bgcolor(q2, color="rgba(255,200,0,0.15)")
bgcolor(q3, color="rgba(255,50,50,0.15)")
bgcolor(q4, color="rgba(100,100,255,0.15)")

# Plot momentum lines
plot(norm_price, title="Price Momentum", color="rgba(0,200,100,0.9)")
plot(norm_vol, title="Volume Momentum", color="rgba(100,150,255,0.9)")

# Zero line
hline(0, title="Zero", color="rgba(150,150,150,0.4)")
