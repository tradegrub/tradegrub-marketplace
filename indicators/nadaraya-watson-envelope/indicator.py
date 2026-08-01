from tg_scripting import *
import numpy as np
from scipy.ndimage import gaussian_filter1d

bandwidth = input.int(8, "Bandwidth", minval=1, maxval=50)
window = input.int(50, "Window", minval=10, maxval=200)
mult = input.float(2.0, "Envelope Multiplier")
atr_len = input.int(14, "ATR Length", minval=1, maxval=50)

c = np.array(close, dtype=float)
n = len(c)

nw = np.zeros(n)
for i in range(n):
    end = min(i + window, n)
    seg = c[i:end]
    indices = np.arange(len(seg))
    weights = np.exp(-0.5 * (indices / bandwidth) ** 2)
    nw[i] = np.sum(seg * weights) / np.sum(weights)

atr_val = ta.atr(high, low, close, atr_len)
upper = nw + mult * np.array(atr_val, dtype=float)
lower = nw - mult * np.array(atr_val, dtype=float)

cross_up = (np.array(close, dtype=float) > upper) & (np.roll(np.array(close, dtype=float), 1) <= np.roll(upper, 1))
cross_dn = (np.array(close, dtype=float) < lower) & (np.roll(np.array(close, dtype=float), 1) >= np.roll(lower, 1))
cross_up[0] = False
cross_dn[0] = False

p_nw = plot(nw, title="NW Regression", color="#ffaa00")
p_upper = plot(upper, title="Upper Envelope", color="#ff4444")
p_lower = plot(lower, title="Lower Envelope", color="#44ff44")
fill(p_upper, p_lower, color="rgba(255,170,0,0.08)")
plotshape(cross_up, title="Overbought", style="triangledown", location="abovebar", color="#ff4444")
plotshape(cross_dn, title="Oversold", style="triangleup", location="belowbar", color="#44ff44")
