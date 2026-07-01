# Bollinger/Keltner Squeeze Momentum Strategy
from tg_scripting import *
import numpy as np

indicator("Squeeze Momentum", overlay=True)

bb_length = input.int(20, "BB Length", minval=5, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=0.5, maxval=4.0)
kc_length = input.int(20, "KC Length", minval=5, maxval=50)
kc_mult = input.float(1.5, "KC Multiplier", minval=0.5, maxval=4.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

squeeze_on, momentum = ta.squeeze(close, high, low, close, bb_length, bb_mult, kc_length, kc_mult)

# Enter long when squeeze fires (was on, now off) and momentum is positive
squeeze_off = squeeze_on[-2] and not squeeze_on[-1]

if squeeze_off and momentum[-1] > 0:
    strategy.entry("Long", strategy.LONG)

# Exit when momentum turns negative
if momentum[-1] < 0 and momentum[-2] >= 0:
    strategy.close("Long")

plot(momentum, title="Momentum", color="teal")
bgcolor(squeeze_on[-1], color="rgba(255,0,0,0.1)")
hline(0, title="Zero", color="gray")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = bb_length
squeeze_label_placed = False

for i in range(bb_length, n):
    # Label squeeze zones
    if show_labels and squeeze_on[i] and not squeeze_label_placed:
        squeeze_start = i
        squeeze_count = 0
        for j in range(i, min(i + bb_length, n)):
            if squeeze_on[j]:
                squeeze_count += 1
        if squeeze_count >= bb_length // 2:
            label.new(x=i, y=float(high[i]), text="Squeeze",
                      style=label.style_label_down, color="rgba(255,152,0,0.3)",
                      textcolor="#ff9800", size="small")
            squeeze_label_placed = True

    if not squeeze_on[i] and i > 0 and squeeze_on[i - 1]:
        squeeze_label_placed = False

    # Label squeeze fire with momentum direction
    if i > 0 and squeeze_on[i - 1] and not squeeze_on[i] and momentum[i] > 0 and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Squeeze Fire\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")

    # Label momentum flip to negative
    if i > 0 and momentum[i] < 0 and momentum[i - 1] >= 0 and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Mom Flip\nEXIT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="small")
