from tg_scripting import *

length = input.int(14, "Length", minval=2, maxval=100)
pct_len = input.int(100, "Percentile Lookback", minval=20, maxval=500)
high_thresh = input.int(80, "High Range Percentile", minval=60, maxval=95)
low_thresh = input.int(20, "Low Range Percentile", minval=5, maxval=40)

hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo
rng_pct = (rng / close) * 100
rng_percentile = ta.percentrank(rng_pct, pct_len)

plot(rng_pct, title="Range %", color="#42A5F5")
plot(rng_percentile, title="Range Percentile", color="#FF7043")
plot(ta.sma(rng_pct, length), title="Avg Range %", color="#AB47BC")

hline(high_thresh, title="Wide Range", color="rgba(239,83,80,0.5)")
hline(low_thresh, title="Narrow Range", color="rgba(38,166,154,0.5)")

bgcolor(rng_percentile > high_thresh, color="rgba(239,83,80,0.06)")
bgcolor(rng_percentile < low_thresh, color="rgba(38,166,154,0.06)")
