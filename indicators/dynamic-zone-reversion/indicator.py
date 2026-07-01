from tg_scripting import *
import numpy as np

indicator("Dynamic Zone Reversion", overlay=False)

osc_len = input.int(14, "Oscillator Length", minval=5, maxval=50)
zone_window = input.int(60, "Zone Adaptation Window", minval=30, maxval=150)
vwap_len = input.int(20, "VWAP Length", minval=10, maxval=50)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, osc_len), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

tp = (hi + lo + cl) / 3.0
cum_tpv = np.cumsum(tp * vol)
cum_vol = np.cumsum(vol)
vwap = np.where(cum_vol > 0, cum_tpv / cum_vol, cl)
vwap_dist = (cl - vwap) / np.maximum(vwap, 1e-10) * 100

osc = (rsi_arr - 50) / 50

dyn_upper = np.zeros(n)
dyn_lower = np.zeros(n)
for i in range(zone_window, n):
    window = osc[i-zone_window:i]
    mu = np.mean(window)
    std = np.std(window)
    dyn_upper[i] = mu + 1.5 * std
    dyn_lower[i] = mu - 1.5 * std

confluence = np.zeros(n)
for i in range(zone_window, n):
    scores = 0
    if osc[i] < dyn_lower[i]:
        scores += 1
    elif osc[i] > dyn_upper[i]:
        scores -= 1
    if vwap_dist[i] < -1:
        scores += 1
    elif vwap_dist[i] > 1:
        scores -= 1
    if i > 0 and cl[i] > cl[i-1]:
        scores += 0.5
    elif i > 0 and cl[i] < cl[i-1]:
        scores -= 0.5
    confluence[i] = scores

bull_zone = (osc < dyn_lower) & (confluence > 0)
bear_zone = (osc > dyn_upper) & (confluence < 0)

plot(osc.tolist(), title="Oscillator", color="#42a5f5", linewidth=2)
plot(dyn_upper.tolist(), title="Upper Zone", color="#f44336", linewidth=1)
plot(dyn_lower.tolist(), title="Lower Zone", color="#4CAF50", linewidth=1)
plot((confluence / 3).tolist(), title="Confluence", color="#ff9800", linewidth=1)
hline(0, title="Zero", color="#888888", linestyle="dashed")
bgcolor(bull_zone.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(bear_zone.tolist(), color="rgba(244,67,54,0.08)")
