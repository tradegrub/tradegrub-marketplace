from tg_scripting import *

fast_len = input.int(20, "Fast MA Length", minval=1, maxval=200)
slow_len = input.int(50, "Slow MA Length", minval=2, maxval=500)
ma_type = input.string("SMA", "MA Type", options=["SMA", "EMA"])

if ma_type == "SMA":
    fast_ma = ta.sma(close, fast_len)
    slow_ma = ta.sma(close, slow_len)
else:
    fast_ma = ta.ema(close, fast_len)
    slow_ma = ta.ema(close, slow_len)

bullish = fast_ma > slow_ma

p1 = plot(fast_ma, title="Fast MA", color="rgba(38,166,154,1)")
p2 = plot(slow_ma, title="Slow MA", color="rgba(239,83,80,1)")

fill_color = np.where(bullish, "rgba(38,166,154,0.15)", "rgba(239,83,80,0.15)")
fill(p1, p2, color=fill_color)
