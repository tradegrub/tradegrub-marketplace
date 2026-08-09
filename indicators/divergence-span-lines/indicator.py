# Divergence Span Lines — the disagreement drawn as a span, not a dot.
from tg_scripting import *
import numpy as np

indicator("Divergence Span Lines", overlay=True)

rsi_length = input.int(21, "RSI length", minval=2, maxval=100)
mom_length = input.int(20, "Momentum length", minval=2, maxval=100)
lookback = input.int(60, "Divergence lookback", minval=10, maxval=300)
upper = input.float(70.0, "Overbought gate", minval=50.0, maxval=95.0)
lower = input.float(30.0, "Oversold gate", minval=5.0, maxval=50.0)
show_lines = input.bool(True, "Draw span lines")

c = np.asarray(close, dtype=float)
h = np.asarray(high, dtype=float)
l = np.asarray(low, dtype=float)
n = len(c)

rsi = ta.rsi(close, rsi_length)
mom = np.full(n, np.nan)
mom[mom_length:] = c[mom_length:] - c[:-mom_length]

bull = np.zeros(n, dtype=bool)
bear = np.zeros(n, dtype=bool)
bull_from = np.full(n, -1, dtype=int)
bear_from = np.full(n, -1, dtype=int)

for i in range(lookback, n):
    window = slice(i - lookback, i)

    # The gate is what separates this from a plain divergence scan: the
    # oscillator has to have actually reached an extreme inside the span,
    # otherwise two mildly disagreeing swings would qualify.
    seg_rsi = rsi[window]
    if not np.isfinite(seg_rsi).any():
        continue

    # Bearish: price took out the window's high while momentum did not.
    j = int(np.nanargmax(h[window])) + i - lookback
    if h[i] > h[j] and np.isfinite(mom[i]) and np.isfinite(mom[j]) and mom[i] < mom[j]:
        if np.nanmax(seg_rsi) >= upper:
            bear[i] = True
            bear_from[i] = j

    # Bullish: price undercut the window's low while momentum held up.
    k = int(np.nanargmin(l[window])) + i - lookback
    if l[i] < l[k] and np.isfinite(mom[i]) and np.isfinite(mom[k]) and mom[i] > mom[k]:
        if np.nanmin(seg_rsi) <= lower:
            bull[i] = True
            bull_from[i] = k

plotshape(bull, title="Bullish divergence", style="triangleup", location="belowbar", color="green")
plotshape(bear, title="Bearish divergence", style="triangledown", location="abovebar", color="red")

if show_lines:
    last_drawn = -100
    for i in range(lookback, n):
        if i - last_drawn < 5:
            continue
        if bull[i] and bull_from[i] >= 0:
            line.new(x1=int(bull_from[i]), y1=float(l[bull_from[i]]), x2=i, y2=float(l[i]),
                     color="#00e676", width=2)
            label.new(x=i, y=float(l[i]), text="DIV", style=label.style_label_up,
                      color="rgba(0,230,118,0.2)", textcolor="#00e676", size="small")
            last_drawn = i
        elif bear[i] and bear_from[i] >= 0:
            line.new(x1=int(bear_from[i]), y1=float(h[bear_from[i]]), x2=i, y2=float(h[i]),
                     color="#ef5350", width=2)
            label.new(x=i, y=float(h[i]), text="DIV", style=label.style_label_down,
                      color="rgba(239,83,80,0.2)", textcolor="#ef5350", size="small")
            last_drawn = i
