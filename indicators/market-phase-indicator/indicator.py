from tg_scripting import *
import numpy as np

indicator("Market Phase Indicator", overlay=False)

length = input.int(20, "Phase Length", minval=10, maxval=50)

cl = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

sma_price = np.array(ta.sma(close, length), dtype=float)
sma_vol = np.array(ta.sma(volume, length), dtype=float)
sma_price = np.nan_to_num(sma_price, nan=0.0)
sma_vol = np.nan_to_num(sma_vol, nan=1.0)

price_trend = np.zeros(n)
vol_trend = np.zeros(n)
for i in range(length, n):
    price_trend[i] = (cl[i] - sma_price[i]) / max(sma_price[i], 1e-10) * 100
    vol_trend[i] = (vol[i] - sma_vol[i]) / max(sma_vol[i], 1e-10) * 100

phase = np.zeros(n)
for i in range(length, n):
    if price_trend[i] > 0 and vol_trend[i] > 0:
        phase[i] = 3  # Markup
    elif price_trend[i] > 0 and vol_trend[i] <= 0:
        phase[i] = 2  # Distribution
    elif price_trend[i] <= 0 and vol_trend[i] > 0:
        phase[i] = 1  # Accumulation
    else:
        phase[i] = 0  # Markdown

markup = phase == 3
distribution = phase == 2
accumulation = phase == 1
markdown = phase == 0

valid = np.arange(n) >= length
plot(phase.tolist(), title="Phase", color="#ffffff", linewidth=2)
hline(3, title="Markup", color="#4CAF50")
hline(2, title="Distribution", color="#ff9800")
hline(1, title="Accumulation", color="#42a5f5")
hline(0, title="Markdown", color="#f44336")

bgcolor((markup & valid).tolist(), color="rgba(76,175,80,0.08)")
bgcolor((distribution & valid).tolist(), color="rgba(255,152,0,0.08)")
bgcolor((accumulation & valid).tolist(), color="rgba(66,165,245,0.08)")
bgcolor((markdown & valid).tolist(), color="rgba(244,67,54,0.08)")
