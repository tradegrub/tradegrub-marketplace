from tg_scripting import *
import numpy as np

indicator("Volume Weighted Momentum", overlay=False)

mom_len = input.int(14, "Momentum Length", minval=2, maxval=50)
vol_len = input.int(20, "Volume MA Length", minval=5, maxval=100)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)
overbought = input.float(1.5, "Overbought", minval=0.5, maxval=5.0, step=0.1)
oversold = input.float(-1.5, "Oversold", minval=-5.0, maxval=-0.5, step=0.1)

n = len(close)
c = np.array(close)
v = np.array(volume)

# Momentum: rate of change
mom = np.zeros(n)
for i in range(mom_len, n):
    if c[i - mom_len] != 0:
        mom[i] = (c[i] - c[i - mom_len]) / c[i - mom_len]

# Relative volume
vol_ma = ta.sma(v, vol_len)
rel_vol = np.where(vol_ma > 0, v / vol_ma, 1.0)

# Volume-weighted momentum
vwm = mom * rel_vol

# Smooth
if smooth > 1:
    vwm_smooth = ta.sma(vwm, smooth)
else:
    vwm_smooth = vwm

# Signal conditions
ob = vwm_smooth > overbought
os_cond = vwm_smooth < oversold

plot(vwm_smooth, title="VW Momentum", color="#42A5F5", linewidth=2)
hline(0, title="Zero", color="#555555", linestyle="dashed")
hline(overbought, title="Overbought", color="rgba(255,23,68,0.5)", linestyle="dashed")
hline(oversold, title="Oversold", color="rgba(0,230,118,0.5)", linestyle="dashed")

bgcolor(ob, color="rgba(255,23,68,0.06)")
bgcolor(os_cond, color="rgba(0,230,118,0.06)")

# Conviction filter: strong trend with volume
strong_bull = (vwm_smooth > 0) & (rel_vol > 1.5)
strong_bear = (vwm_smooth < 0) & (rel_vol > 1.5)

plotshape(strong_bull, title="Strong Bull", shape="triangleup", location="belowbar", color="#00e676", size="tiny")
plotshape(strong_bear, title="Strong Bear", shape="triangledown", location="abovebar", color="#ff1744", size="tiny")
