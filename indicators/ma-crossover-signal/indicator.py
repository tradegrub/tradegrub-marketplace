from tg_scripting import *

fast_len = input.int(9, "Fast MA Length", minval=1, maxval=100)
slow_len = input.int(21, "Slow MA Length", minval=2, maxval=300)
ma_type = input.string("EMA", "MA Type", options=["SMA", "EMA", "WMA", "HMA"])

if ma_type == "SMA":
    fast_ma = ta.sma(close, fast_len)
    slow_ma = ta.sma(close, slow_len)
elif ma_type == "EMA":
    fast_ma = ta.ema(close, fast_len)
    slow_ma = ta.ema(close, slow_len)
elif ma_type == "WMA":
    fast_ma = ta.wma(close, fast_len)
    slow_ma = ta.wma(close, slow_len)
else:
    fast_ma = ta.hma(close, fast_len)
    slow_ma = ta.hma(close, slow_len)

cross_up = ta.crossover(fast_ma, slow_ma)
cross_down = ta.crossunder(fast_ma, slow_ma)

plot(fast_ma, title="Fast MA", color="rgba(38,166,154,1)")
plot(slow_ma, title="Slow MA", color="rgba(239,83,80,1)")

plotshape(cross_up, title="Bullish Cross", style="triangleup", location="belowbar", color="green", size="small")
plotshape(cross_down, title="Bearish Cross", style="triangledown", location="abovebar", color="red", size="small")
