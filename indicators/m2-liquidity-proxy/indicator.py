from tg_scripting import *
import numpy as np

lookback = input.int(50, "Lookback", minval=10, maxval=200)

src_close = np.array(close, dtype=float)
src_open = np.array(open, dtype=float)
src_vol = np.array(volume, dtype=float)
n = len(src_close)

# Signed volume: volume * sign(close - open)
price_direction = np.sign(src_close - src_open)
signed_vol = src_vol * price_direction

# Cumulative signed volume (liquidity flow)
cum_signed_vol = np.cumsum(signed_vol)

# Normalize by rolling average volume
avg_vol = np.empty(n, dtype=float)
for i in range(n):
    start = max(0, i - lookback + 1)
    avg_vol[i] = np.mean(src_vol[start:i + 1])

# Normalized liquidity flow
liq_flow = np.zeros(n, dtype=float)
for i in range(n):
    start = max(0, i - lookback + 1)
    window_cum = np.cumsum(signed_vol[start:i + 1])
    if avg_vol[i] > 0:
        liq_flow[i] = window_cum[-1] / (avg_vol[i] * lookback) * 100.0

# SMA of liquidity flow
sma_liq = np.empty(n, dtype=float)
sma_period = min(20, lookback)
for i in range(n):
    start = max(0, i - sma_period + 1)
    sma_liq[i] = np.mean(liq_flow[start:i + 1])

plot(liq_flow, title="Liquidity Flow", color="#26c6da")
plot(sma_liq, title="Liquidity SMA", color="#ff7043")
hline(0, title="Zero", color="#555555")

bgcolor(liq_flow > 0, color="rgba(38,198,218,0.08)")
bgcolor(liq_flow < 0, color="rgba(255,112,67,0.08)")
