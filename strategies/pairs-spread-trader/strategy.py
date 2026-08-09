# Pairs Spread Trader — the charted symbol is leg one, the partner is leg two.
from tg_scripting import *
import numpy as np

indicator("Pairs Spread Trader", overlay=True)

partner = input.string("SPY", "Partner symbol")
window = input.int(60, "Spread window", minval=20, maxval=400)
entry_z = input.float(2.0, "Entry z-score", minval=0.5, maxval=5.0)
exit_z = input.float(0.5, "Exit z-score", minval=0.0, maxval=3.0)
stop_z = input.float(4.0, "Stop z-score", minval=1.0, maxval=10.0)

c = np.asarray(close, dtype=float)
n = len(c)

leg2 = np.asarray(request.security(partner, timeframe.period, "close"), dtype=float)
if leg2.shape[0] != n:
    leg2 = np.full(n, np.nan)

spread_z = np.full(n, np.nan)
hedge = np.full(n, np.nan)

for i in range(window, n):
    a = c[i - window + 1:i + 1]
    b = leg2[i - window + 1:i + 1]
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        continue
    var_b = float(np.var(b))
    if var_b <= 0:
        continue
    # Hedge ratio from a rolling regression, so the spread stays dollar-neutral
    # as the relationship drifts rather than assuming a fixed 1:1.
    beta = float(np.cov(a, b, bias=True)[0, 1]) / var_b
    resid = a - beta * b
    sd = float(np.std(resid))
    if sd <= 0:
        continue
    hedge[i] = beta
    spread_z[i] = (resid[-1] - float(np.mean(resid))) / sd

side = 0
long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
flat_sig = np.zeros(n, dtype=bool)

for i in range(window, n):
    strategy.set_bar_index(i)
    z = spread_z[i]
    if not np.isfinite(z):
        continue

    if side == 0:
        # Spread cheap: the charted leg is the underperformer, so buy it.
        if z <= -entry_z:
            strategy.entry("Long", strategy.LONG)
            side, long_sig[i] = 1, True
        elif z >= entry_z:
            strategy.entry("Short", strategy.SHORT)
            side, short_sig[i] = -1, True
    elif side == 1:
        if z >= -exit_z or z <= -stop_z:
            strategy.close("Long")
            side, flat_sig[i] = 0, True
    else:
        if z <= exit_z or z >= stop_z:
            strategy.close("Short")
            side, flat_sig[i] = 0, True

plotshape(long_sig, title="Spread cheap, long leg 1", style="triangleup", location="belowbar", color="green")
plotshape(short_sig, title="Spread rich, short leg 1", style="triangledown", location="abovebar", color="red")
plotshape(flat_sig, title="Spread reverted", style="xcross", location="abovebar", color="gray")
