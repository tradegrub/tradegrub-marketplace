from tg_scripting import *
import numpy as np

indicator("Enhanced Momentum Scanner", overlay=False)

length = input.int(14, "Momentum Length", minval=5, maxval=50)
smooth = input.int(5, "Smoothing", minval=2, maxval=15)
div_lookback = input.int(30, "Divergence Lookback", minval=10, maxval=60)

cl = np.array(close, dtype=float)
n = len(cl)

raw_mom = np.zeros(n)
for i in range(length, n):
    raw_mom[i] = (cl[i] - cl[i-length]) / max(cl[i-length], 1e-10) * 100

mom = np.copy(raw_mom)
alpha = 2.0 / (smooth + 1)
for _ in range(3):
    temp = np.copy(mom)
    for i in range(1, n):
        temp[i] = alpha * mom[i] + (1 - alpha) * temp[i-1]
    mom = temp

quality = np.zeros(n)
for i in range(20, n):
    window = mom[i-20:i+1]
    trend = np.polyfit(np.arange(21), window, 1)[0]
    noise = np.std(window - np.polyval(np.polyfit(np.arange(21), window, 1), np.arange(21)))
    if noise > 0:
        quality[i] = min(abs(trend) / noise * 30, 100)

bull_div = np.zeros(n, dtype=bool)
bear_div = np.zeros(n, dtype=bool)
for i in range(div_lookback, n):
    if cl[i] < cl[i-div_lookback] and mom[i] > mom[i-div_lookback]:
        bull_div[i] = True
    elif cl[i] > cl[i-div_lookback] and mom[i] < mom[i-div_lookback]:
        bear_div[i] = True

plot(mom.tolist(), title="Smooth Momentum", color="#e040fb", linewidth=2)
plot(quality.tolist(), title="Signal Quality", color="#78909C", linewidth=1)
hline(0, title="Zero", color="#888888", linestyle="dashed")
plotshape(bull_div.tolist(), title="Bull Div", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bear_div.tolist(), title="Bear Div", style="triangledown", location="abovebar", color="#ff1744", size="small")
