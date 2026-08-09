# Mansfield Relative Strength — the zero line is the whole point.
from tg_scripting import *
import numpy as np

indicator("Mansfield RS", overlay=False)

benchmark = input.string("SPY", "Benchmark symbol")
ma_length = input.int(52, "Zero-line MA length", minval=10, maxval=300)
scale_factor = input.float(10.0, "Scale", minval=1.0, maxval=100.0)

c = np.asarray(close, dtype=float)
n = len(c)

bench = np.asarray(request.security(benchmark, timeframe.period, "close"), dtype=float)
if bench.shape[0] != n:
    bench = np.full(n, np.nan)

with np.errstate(divide="ignore", invalid="ignore"):
    rp = np.where(bench != 0, c / bench, np.nan)

rp_ma = ta.sma(rp, ma_length)

# Mansfield expresses the ratio as a percentage deviation from its own average,
# so zero means "performing exactly in line with the market over that window".
with np.errstate(divide="ignore", invalid="ignore"):
    mansfield = np.where(rp_ma != 0, (rp / rp_ma - 1.0) * 100 * scale_factor / 10.0, np.nan)

plot(mansfield, title="Mansfield RS", color="blue")
hline(0.0, title="Market line", color="orange")

positive = mansfield > 0
plotshape(positive & ~np.roll(positive, 1), title="Crosses above zero", style="triangleup",
          location="belowbar", color="green")
plotshape(~positive & np.roll(positive, 1), title="Crosses below zero", style="triangledown",
          location="abovebar", color="red")
