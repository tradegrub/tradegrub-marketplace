# Price Relative — the ratio line, not another oscillator.
from tg_scripting import *
import numpy as np

indicator("Price Relative", overlay=False)

benchmark = input.string("SPY", "Benchmark symbol")
ma_length = input.int(50, "Ratio MA length", minval=2, maxval=400)
normalize = input.bool(True, "Rebase to 100 at the first bar")

c = np.asarray(close, dtype=float)
n = len(c)

# request.security pulls the benchmark on the chart's own timeframe. With no
# benchmark data available the series is nan, and the script must stay quiet
# rather than plotting a misleading flat line.
bench = np.asarray(request.security(benchmark, timeframe.period, "close"), dtype=float)
if bench.shape[0] != n:
    bench = np.full(n, np.nan)

with np.errstate(divide="ignore", invalid="ignore"):
    ratio = np.where(bench != 0, c / bench, np.nan)

if normalize:
    valid = np.flatnonzero(np.isfinite(ratio))
    if valid.size:
        base = ratio[valid[0]]
        if base != 0:
            ratio = ratio / base * 100

ratio_ma = ta.sma(ratio, ma_length)

plot(ratio, title="Price relative", color="blue")
plot(ratio_ma, title="Ratio MA", color="orange")

# Leadership is the ratio above its own average, which is a cleaner read than
# the raw slope of a noisy ratio line.
leading = ratio > ratio_ma
plotshape(leading & ~np.roll(leading, 1), title="Turns leader", style="triangleup",
          location="belowbar", color="green")
plotshape(~leading & np.roll(leading, 1), title="Turns laggard", style="triangledown",
          location="abovebar", color="red")
