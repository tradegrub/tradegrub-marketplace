# Gap Fill Reversion Strategy
from tg_scripting import *

min_gap_atr = input.float(0.5, "Min Gap Size (ATR mult)", minval=0.2, maxval=3.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_stop = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
max_bars = input.int(10, "Max Bars to Fill", minval=3, maxval=30)

atr = ta.atr(high, low, close, atr_len)

# Detect gap: current open vs previous close
gap_up = open[-1] - close[-2]
gap_down = close[-2] - open[-1]

# Gap up: open above prior close by at least min_gap_atr * ATR
is_gap_up = gap_up > atr[-2] * min_gap_atr
# Gap down: open below prior close by at least min_gap_atr * ATR
is_gap_down = gap_down > atr[-2] * min_gap_atr

# Fade the gap: expect price to fill back toward prior close
if is_gap_up:
    # Short the gap up, target prior close
    strategy.entry("Short Gap", strategy.SHORT)
    strategy.exit("Short Exit", "Short Gap",
                  limit=close[-2],
                  stop=open[-1] + atr[-1] * atr_stop)

if is_gap_down:
    # Long the gap down, target prior close
    strategy.entry("Long Gap", strategy.LONG)
    strategy.exit("Long Exit", "Long Gap",
                  limit=close[-2],
                  stop=open[-1] - atr[-1] * atr_stop)

# Time-based exit: close if gap hasn't filled within max_bars
bars_since_gap_up = ta.barsince(is_gap_up)
bars_since_gap_down = ta.barsince(is_gap_down)

if bars_since_gap_up[-1] == max_bars:
    strategy.close("Short Gap")
if bars_since_gap_down[-1] == max_bars:
    strategy.close("Long Gap")

# Plot gap levels
gap_size = open - np.roll(close, 1)
plot(gap_size, title="Gap Size", color="purple")
hline(0, title="Zero Line", color="gray")
plotshape(is_gap_up, title="Gap Up", style="triangledown", location="abovebar", color="red")
plotshape(is_gap_down, title="Gap Down", style="triangleup", location="belowbar", color="green")
