from tg_scripting import *

length = input.int(20, "Length", minval=5, maxval=200)
ob_level = input.float(2.0, "Overbought Z-Score", minval=0.5, maxval=4.0)
os_level = input.float(-2.0, "Oversold Z-Score", minval=-4.0, maxval=-0.5)

sma_val = ta.sma(close, length)
stdev_val = ta.stdev(close, length)
zscore = (close - sma_val) / stdev_val

plot(zscore, title="Z-Score", color="#7E57C2")
h_ob = hline(ob_level, title="Overbought", color="rgba(239,83,80,0.5)")
h_os = hline(os_level, title="Oversold", color="rgba(38,166,154,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.4)")
fill(h_ob, h_os, color="rgba(126,87,194,0.05)")

bgcolor(zscore > ob_level, color="rgba(239,83,80,0.08)")
bgcolor(zscore < os_level, color="rgba(38,166,154,0.08)")
