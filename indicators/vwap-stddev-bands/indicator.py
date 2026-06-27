from tg_scripting import *

length = input.int("Length", 14, minval=1, maxval=200)
mult = input.float("StdDev Multiplier", 2.0, minval=0.5, maxval=5.0)

vwap_val = ta.vwap(close, volume)
basis = ta.sma(close, length)
dev = mult * ta.stdev(close, length)

upper = vwap_val + dev
lower = vwap_val - dev

plot(vwap_val, "VWAP", color="blue")
plot(upper, "Upper Band", color="rgba(38,166,154,0.5)")
plot(lower, "Lower Band", color="rgba(239,83,80,0.5)")
fill(upper, lower, color="rgba(38,166,154,0.08)")
