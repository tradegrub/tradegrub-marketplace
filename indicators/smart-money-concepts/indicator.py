from tg_scripting import *

swing_length = input.int(5, "Swing Length", minval=2, maxval=20)
show_bos = input.bool(True, "Show Break of Structure")
show_fvg = input.bool(True, "Show Fair Value Gaps")

swing_high = ta.highest(high, swing_length)
swing_low = ta.lowest(low, swing_length)

prev_high = swing_high[swing_length]
prev_low = swing_low[swing_length]

if show_bos:
    bos_up = ta.crossover(close, prev_high)
    bos_down = ta.crossunder(close, prev_low)
    plotshape(bos_up, title="BOS Up", shape="triangleup", location="abovebar", color="green", size="small")
    plotshape(bos_down, title="BOS Down", shape="triangledown", location="belowbar", color="red", size="small")

if show_fvg:
    fvg_bull = low > high[2]
    fvg_bear = high < low[2]
    bgcolor(fvg_bull, color="rgba(38,166,154,0.1)")
    bgcolor(fvg_bear, color="rgba(239,83,80,0.1)")

plot(swing_high, title="Swing High", color="rgba(38,166,154,0.4)", linewidth=1)
plot(swing_low, title="Swing Low", color="rgba(239,83,80,0.4)", linewidth=1)
