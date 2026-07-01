from tg_scripting import *
import numpy as np

indicator("Causal Adaptive Smoother", overlay=True)

base_length = input.int(20, "Base Length", minval=5, maxval=100)
sensitivity = input.float(1.5, "Sensitivity", minval=0.1, maxval=5.0)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

# ATR-based volatility
atr_vals = np.array(ta.atr(high, low, close, base_length), dtype=float)
atr_sma = np.array(ta.sma(atr_vals.tolist(), base_length), dtype=float)

# Volatility ratio: current ATR / average ATR
vol_ratio = np.where(atr_sma == 0, 1.0, atr_vals / atr_sma)

# Adaptive alpha: higher alpha (faster) when volatility is low
base_alpha = 2.0 / (base_length + 1)
adaptive_alpha = np.clip(base_alpha * (1.0 + sensitivity * (1.0 - vol_ratio)), 0.01, 0.99)

# Apply exponential filter with adaptive alpha
smoothed = np.full(n, np.nan)
smoothed[0] = src[0]
for i in range(1, n):
    alpha = float(adaptive_alpha[i]) if not np.isnan(adaptive_alpha[i]) else base_alpha
    prev = float(smoothed[i - 1]) if not np.isnan(smoothed[i - 1]) else src[i]
    smoothed[i] = alpha * src[i] + (1.0 - alpha) * prev

# Direction coloring
direction = np.where(smoothed > np.roll(smoothed, 1), 1, -1)
direction[0] = 0
colors = np.where(direction > 0, "#4CAF50", "#f44336").tolist()

plot(smoothed.tolist(), title="Adaptive Smooth", color=colors)
