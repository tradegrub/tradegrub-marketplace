from tg_scripting import *
import numpy as np

indicator("Premium Discount Zones", overlay=True)

range_len = input.int(50, "Range Length", minval=10, maxval=200)
eq_band = input.float(0.1, "Equilibrium Band %", minval=0.01, maxval=0.3, step=0.01)
show_eq = input.bool(True, "Show Equilibrium")
show_labels = input.bool(True, "Show Zone Labels")

n = len(close)
range_high = ta.highest(high, range_len)
range_low = ta.lowest(low, range_len)
midpoint = (np.array(range_high) + np.array(range_low)) / 2.0
rng = np.array(range_high) - np.array(range_low) + 1e-10

# Position in range: 0=bottom, 1=top
position = (np.array(close) - np.array(range_low)) / rng

premium = position > (0.5 + eq_band)
discount = position < (0.5 - eq_band)
equilibrium = ~premium & ~discount

eq_top = midpoint + rng * eq_band
eq_bot = midpoint - rng * eq_band

plot(range_high, title="Range High", color="rgba(255,23,68,0.5)", linewidth=1, style="stepline")
plot(range_low, title="Range Low", color="rgba(0,230,118,0.5)", linewidth=1, style="stepline")
plot(midpoint, title="Equilibrium", color="rgba(255,255,255,0.3)", linewidth=1, style="dashed")

if show_eq:
    plot(eq_top, title="EQ Upper", color="rgba(255,255,255,0.15)", linewidth=1)
    plot(eq_bot, title="EQ Lower", color="rgba(255,255,255,0.15)", linewidth=1)

bgcolor(premium, color="rgba(255,23,68,0.05)")
bgcolor(discount, color="rgba(0,230,118,0.05)")
bgcolor(equilibrium, color="rgba(255,255,255,0.02)")

if show_labels:
    last_lbl = -30
    for i in range(range_len, n):
        if i - last_lbl < 30:
            continue
        if premium[i] and (not premium[i - 1] if i > 0 else True):
            label.new(x=i, y=float(high[i]), text="Premium",
                      style=label.style_label_down, color="rgba(255,23,68,0.4)",
                      textcolor="#ff1744", size="tiny")
            last_lbl = i
        elif discount[i] and (not discount[i - 1] if i > 0 else True):
            label.new(x=i, y=float(low[i]), text="Discount",
                      style=label.style_label_up, color="rgba(0,230,118,0.4)",
                      textcolor="#00e676", size="tiny")
            last_lbl = i
