from tg_scripting import *
import numpy as np

indicator("Cumulative Delta Volume", overlay=False)

smooth_len = input.int(5, "Smoothing Length", minval=1, maxval=20)
show_zero = input.bool(True, "Show Zero Line")
show_ma = input.bool(True, "Show Moving Average")
ma_len = input.int(14, "MA Length", minval=5, maxval=50)

n = len(close)
c = np.array(close)
o = np.array(open)
h = np.array(high)
l = np.array(low)
v = np.array(volume)

# Estimate buy/sell volume using candle position
rng = h - l + 1e-10
buy_pct = (c - l) / rng
sell_pct = (h - c) / rng

buy_vol = v * buy_pct
sell_vol = v * sell_pct
delta = buy_vol - sell_vol

# Cumulative delta
cum_delta = np.cumsum(delta)

# Smooth
if smooth_len > 1:
    cum_delta_smooth = ta.sma(cum_delta, smooth_len)
else:
    cum_delta_smooth = cum_delta

# Color based on direction
rising = np.zeros(n, dtype=bool)
falling = np.zeros(n, dtype=bool)
for i in range(1, n):
    if cum_delta_smooth[i] > cum_delta_smooth[i - 1]:
        rising[i] = True
    else:
        falling[i] = True

plot(cum_delta_smooth, title="Cum Delta", color="#42A5F5", linewidth=2)

if show_ma:
    cd_ma = ta.sma(cum_delta_smooth, ma_len)
    plot(cd_ma, title="Delta MA", color="#ff9800", linewidth=1)

if show_zero:
    hline(0, title="Zero", color="#555555", linestyle="dashed")


# Divergence detection: price rising but delta falling
price_rising = c > ta.sma(c, 14)
delta_falling = cum_delta_smooth < ta.sma(cum_delta_smooth, 14)
bear_div = price_rising & delta_falling

price_falling = c < ta.sma(c, 14)
delta_rising = cum_delta_smooth > ta.sma(cum_delta_smooth, 14)
bull_div = price_falling & delta_rising

plotshape(bear_div, title="Bear Divergence", shape="triangledown", location="abovebar", color="#ff1744", size="tiny")
plotshape(bull_div, title="Bull Divergence", shape="triangleup", location="belowbar", color="#00e676", size="tiny")
