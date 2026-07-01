from tg_scripting import *
import numpy as np

indicator("Relative Volume Indicator", overlay=False)

avg_len = input.int(20, "Average Length", minval=5, maxval=100)
spike_mult = input.float(2.0, "Spike Threshold", minval=1.0, maxval=5.0, step=0.1)
low_mult = input.float(0.5, "Low Volume Threshold", minval=0.1, maxval=1.0, step=0.1)
smooth = input.int(1, "Smoothing", minval=1, maxval=10)

n = len(close)
v = np.array(volume)
vol_ma = ta.sma(v, avg_len)

rvol = np.where(vol_ma > 0, v / vol_ma, 1.0)

if smooth > 1:
    rvol = ta.sma(rvol, smooth)

spike = rvol > spike_mult
low_vol = rvol < low_mult

plot(rvol, title="RVOL", color="#42A5F5", linewidth=2)
hline(1.0, title="Average", color="#888888", linestyle="dashed")
hline(spike_mult, title="Spike Level", color="rgba(255,23,68,0.5)", linestyle="dashed")
hline(low_mult, title="Low Level", color="rgba(255,171,0,0.5)", linestyle="dashed")

bgcolor(spike, color="rgba(0,230,118,0.08)")
bgcolor(low_vol, color="rgba(255,171,0,0.05)")

plotshape(spike, title="Volume Spike", shape="triangleup", location="belowbar", color="#00e676", size="small")

# Price direction on spike
bull_spike = spike & (np.array(close) > np.array(open))
bear_spike = spike & (np.array(close) < np.array(open))

plotshape(bull_spike, title="Bull Spike", shape="diamond", location="abovebar", color="#00e676", size="tiny")
plotshape(bear_spike, title="Bear Spike", shape="diamond", location="abovebar", color="#ff1744", size="tiny")
