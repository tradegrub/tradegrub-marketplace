from tg_scripting import *
import numpy as np

indicator("Volume Climax Detector", overlay=False)

vol_len = input.int(20, "Volume MA Length", minval=5, maxval=100)
climax_mult = input.float(3.0, "Climax Multiplier", minval=1.5, maxval=10.0, step=0.5)
wick_pct = input.float(0.5, "Min Wick Ratio", minval=0.2, maxval=0.9, step=0.05)
show_labels = input.bool(True, "Show Labels")

n = len(close)
v = np.array(volume)
c = np.array(close)
o = np.array(open)
h = np.array(high)
l = np.array(low)

vol_ma = ta.sma(v, vol_len)
climax_vol = v > (vol_ma * climax_mult)

body = np.abs(c - o)
total_range = h - l + 1e-10
upper_wick = h - np.maximum(c, o)
lower_wick = np.minimum(c, o) - l

# Exhaustion: climax volume with large wicks (rejection)
upper_wick_ratio = upper_wick / total_range
lower_wick_ratio = lower_wick / total_range

bear_climax = climax_vol & (upper_wick_ratio >= wick_pct)
bull_climax = climax_vol & (lower_wick_ratio >= wick_pct)

# Capitulation: climax volume with large body (full surrender)
body_ratio = body / total_range
capitulation_sell = climax_vol & (body_ratio > 0.7) & (c < o)
capitulation_buy = climax_vol & (body_ratio > 0.7) & (c > o)

plotshape(bear_climax, title="Bear Climax", shape="triangledown", location="abovebar", color="#ff1744", size="small")
plotshape(bull_climax, title="Bull Climax", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(capitulation_sell, title="Sell Capitulation", shape="xcross", location="abovebar", color="#ff9800", size="small")
plotshape(capitulation_buy, title="Buy Capitulation", shape="xcross", location="belowbar", color="#ffab00", size="small")

bgcolor(bear_climax, color="rgba(255,23,68,0.06)")
bgcolor(bull_climax, color="rgba(0,230,118,0.06)")
bgcolor(capitulation_sell, color="rgba(255,152,0,0.06)")

plot(v / vol_ma, title="Volume Ratio", color="#42A5F5", display="none")

if show_labels:
    last_lbl = -15
    for i in range(vol_len, n):
        if i - last_lbl < 15:
            continue
        if bear_climax[i]:
            label.new(x=i, y=float(h[i]), text="Climax",
                      style=label.style_label_down, color="rgba(255,23,68,0.5)",
                      textcolor="#ff1744", size="tiny")
            last_lbl = i
        elif bull_climax[i]:
            label.new(x=i, y=float(l[i]), text="Climax",
                      style=label.style_label_up, color="rgba(0,230,118,0.5)",
                      textcolor="#00e676", size="tiny")
            last_lbl = i
        elif capitulation_sell[i]:
            label.new(x=i, y=float(h[i]), text="Capit",
                      style=label.style_label_down, color="rgba(255,152,0,0.5)",
                      textcolor="#ff9800", size="tiny")
            last_lbl = i
