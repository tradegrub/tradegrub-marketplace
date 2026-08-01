from tg_scripting import *
import numpy as np

indicator("Volume Surge Mapper", overlay=False)

length = input.int(20, "Lookback Length", minval=10, maxval=100)
moderate_z = input.float(1.5, "Moderate Threshold (z)", minval=1.0, maxval=3.0, step=0.25)
strong_z = input.float(2.5, "Strong Threshold (z)", minval=2.0, maxval=4.0, step=0.25)

vol = np.array(volume, dtype=float)
cl = np.array(close, dtype=float)
op = np.array(open, dtype=float)
n = len(cl)

z_score = np.zeros(n)
vol_ratio = np.zeros(n)

for i in range(length, n):
    window = vol[i-length:i]
    mu = np.mean(window)
    sigma = np.std(window)
    if sigma > 0:
        z_score[i] = (vol[i] - mu) / sigma
    vol_ratio[i] = vol[i] / max(mu, 1e-10)

bullish_dir = cl > op
moderate_surge = z_score > moderate_z
strong_surge = z_score > strong_z

plot(z_score.tolist(), title="Volume Z-Score", color="#42a5f5", linewidth=2)
plot(vol_ratio.tolist(), title="Volume Ratio", color="#78909C", linewidth=1)
hline(moderate_z, title="Moderate", color="#ff9800", linestyle="dashed")
hline(strong_z, title="Strong", color="#f44336", linestyle="dashed")
hline(0, title="Zero", color="#888888", linestyle="dashed")

bull_surge = (moderate_surge & bullish_dir).tolist()
bear_surge = (moderate_surge & ~bullish_dir).tolist()
bgcolor(bull_surge, color="rgba(76,175,80,0.08)")
bgcolor(bear_surge, color="rgba(244,67,54,0.08)")

plotshape(strong_surge.tolist(), title="Strong Surge", style="triangleup", location="belowbar", color="#ff1744", size="small")
