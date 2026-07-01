from tg_scripting import *
import numpy as np

indicator("Displacement Detector", overlay=True)

body_mult = input.float(1.5, "Body Size Multiplier", minval=1.0, maxval=5.0, step=0.1)
consec = input.int(2, "Consecutive Candles", minval=1, maxval=5)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
show_labels = input.bool(True, "Show Labels")

n = len(close)
atr = ta.atr(high, low, close, atr_len)

body = np.abs(np.array(close) - np.array(open))
bullish = np.array(close) > np.array(open)
bearish = np.array(close) < np.array(open)

# Large body relative to ATR
large_body = body > (np.array(atr) * body_mult)

# Count consecutive large bullish/bearish candles
bull_disp = np.zeros(n, dtype=bool)
bear_disp = np.zeros(n, dtype=bool)

for i in range(consec - 1, n):
    bull_run = True
    bear_run = True
    for j in range(consec):
        idx = i - j
        if not (large_body[idx] and bullish[idx]):
            bull_run = False
        if not (large_body[idx] and bearish[idx]):
            bear_run = False
    bull_disp[i] = bull_run
    bear_disp[i] = bear_run

# Displacement strength: sum of body sizes in the run
strength = np.zeros(n)
for i in range(consec - 1, n):
    if bull_disp[i] or bear_disp[i]:
        s = sum(body[i - j] for j in range(consec))
        strength[i] = s

bgcolor(bull_disp, color="rgba(0,230,118,0.08)")
bgcolor(bear_disp, color="rgba(255,23,68,0.08)")

plotshape(bull_disp, title="Bull Displacement", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bear_disp, title="Bear Displacement", shape="triangledown", location="abovebar", color="#ff1744", size="small")

plot(strength, title="Displacement Strength", color="#42A5F5", display="none")

if show_labels:
    last_lbl = -15
    for i in range(consec, n):
        if i - last_lbl < 15:
            continue
        if bull_disp[i]:
            label.new(x=i, y=float(low[i]), text="Disp",
                      style=label.style_label_up, color="rgba(0,230,118,0.4)",
                      textcolor="#00e676", size="tiny")
            last_lbl = i
        elif bear_disp[i]:
            label.new(x=i, y=float(high[i]), text="Disp",
                      style=label.style_label_down, color="rgba(255,23,68,0.4)",
                      textcolor="#ff1744", size="tiny")
            last_lbl = i
