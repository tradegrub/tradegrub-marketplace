from tg_scripting import *

swing_length = input.int(5, "Swing Length", minval=2, maxval=20)
show_ob = input.bool(True, "Show Order Blocks")
show_fvg = input.bool(True, "Show Fair Value Gaps")
show_bos = input.bool(True, "Show Break of Structure")

swing_high = ta.highest(high, swing_length)
swing_low = ta.lowest(low, swing_length)

prev_high = swing_high[swing_length]
prev_low = swing_low[swing_length]

if show_bos and close > prev_high:
    plotshape(high, "BOS Up", shape="triangleup", location="abovebar", color="green", size="small")
if show_bos and close < prev_low:
    plotshape(low, "BOS Down", shape="triangledown", location="belowbar", color="red", size="small")

if show_fvg and low > high[2]:
    bgcolor("rgba(38,166,154,0.1)")
if show_fvg and high < low[2]:
    bgcolor("rgba(239,83,80,0.1)")

plot(swing_high, "Swing High", color="rgba(38,166,154,0.4)", linewidth=1)
plot(swing_low, "Swing Low", color="rgba(239,83,80,0.4)", linewidth=1)
