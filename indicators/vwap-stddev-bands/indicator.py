from tg_scripting import *

length = input.int(14, "Length", minval=1, maxval=200)
mult = input.float(2.0, "StdDev Multiplier", minval=0.5, maxval=5.0)

vwap_val = ta.vwap(high, low, close, volume)
basis = ta.sma(close, length)
dev = mult * ta.stdev(close, length)

upper = vwap_val + dev
lower = vwap_val - dev

plot(vwap_val, title="VWAP", color="blue")
plot(upper, title="Upper Band", color="rgba(38,166,154,0.5)")
plot(lower, title="Lower Band", color="rgba(239,83,80,0.5)")
fill(upper, lower, color="rgba(38,166,154,0.08)")
