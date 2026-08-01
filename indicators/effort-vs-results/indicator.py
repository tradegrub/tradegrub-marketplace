from tg_scripting import *
import numpy as np

length = input.int(14, "Length", minval=2, maxval=100)

ln = int(length)

# Effort: volume normalized by its SMA
vol_sma = ta.sma(volume, ln)
effort = np.array(volume[:ln * 3], dtype=float) / np.maximum(np.array(vol_sma[:ln * 3], dtype=float), 1e-10)

# Result: absolute price change normalized by ATR
price_change = np.abs(np.array(close[:ln * 3], dtype=float) - np.array(close[1:ln * 3 + 1], dtype=float))
atr_val = ta.atr(high, low, close, ln)
atr_arr = np.maximum(np.array(atr_val[:ln * 3], dtype=float), 1e-10)
result = price_change / atr_arr

# E/R ratio: result per unit of effort
er_ratio_arr = result / np.maximum(effort, 1e-10)

# Build full-length arrays
er_ratio = np.full(len(close), np.nan)
er_ratio[:len(er_ratio_arr)] = er_ratio_arr

# Signal line: SMA of E/R ratio
er_signal = ta.sma(er_ratio, ln)

plot(er_ratio, title="E/R Ratio", color=color.aqua)
plot(er_signal, title="Signal", color=color.orange)
hline(1.0, title="Equilibrium", color=color.gray)
bgcolor(er_ratio < 0.5, color="rgba(255,82,82,0.08)")
