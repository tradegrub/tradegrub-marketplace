from tg_scripting import *
import numpy as np

indicator("Traders Dynamic Index", overlay=False)

rsi_len = input.int(13, "RSI Length", minval=2, maxval=50)
bb_len = input.int(34, "Band Length", minval=5, maxval=100)
bb_mult = input.float(1.6185, "Band Multiplier", minval=0.5, maxval=4.0, step=0.1)
fast_len = input.int(2, "Fast MA Length", minval=1, maxval=20)
slow_len = input.int(7, "Slow MA Length", minval=2, maxval=50)

# RSI
rsi = np.array(ta.rsi(close, rsi_len))

# Bollinger Bands on RSI
bb_upper, bb_mid, bb_lower = ta.bb(rsi.tolist(), bb_len, bb_mult)
bb_upper = np.array(bb_upper)
bb_mid = np.array(bb_mid)
bb_lower = np.array(bb_lower)

# Fast and slow MA of RSI
fast_ma = np.array(ta.sma(rsi.tolist(), fast_len))
slow_ma = np.array(ta.sma(rsi.tolist(), slow_len))

# Cross signals
cross_up = np.zeros(len(close), dtype=bool)
cross_down = np.zeros(len(close), dtype=bool)
for i in range(1, len(close)):
    if fast_ma[i] > slow_ma[i] and fast_ma[i - 1] <= slow_ma[i - 1]:
        cross_up[i] = True
    elif fast_ma[i] < slow_ma[i] and fast_ma[i - 1] >= slow_ma[i - 1]:
        cross_down[i] = True

# Plots
plot(bb_upper.tolist(), title="Upper Band", color="rgba(66,165,245,0.4)", linewidth=1)
plot(bb_lower.tolist(), title="Lower Band", color="rgba(66,165,245,0.4)", linewidth=1)
plot(bb_mid.tolist(), title="Mid Band", color="#FFB74D", linewidth=1)
plot(fast_ma.tolist(), title="Fast MA", color="#00e676", linewidth=2)
plot(slow_ma.tolist(), title="Slow MA", color="#ff1744", linewidth=2)
hline(68.0, title="Overbought", color="#ef5350", linestyle="dashed")
hline(32.0, title="Oversold", color="#26a69a", linestyle="dashed")
hline(50.0, title="Midline", color="#555555", linestyle="dashed")
plotshape(cross_up, title="Bull Cross", style="triangleup", location="belowbar", color="#00e676")
plotshape(cross_down, title="Bear Cross", style="triangledown", location="abovebar", color="#ff1744")
