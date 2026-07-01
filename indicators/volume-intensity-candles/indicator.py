from tg_scripting import *
import numpy as np

indicator("Volume Intensity Candles", overlay=True)

length = input.int(20, "Volume Lookback", minval=10, maxval=100)
high_pct = input.int(80, "High Volume Percentile", minval=60, maxval=95)

vol = np.array(volume, dtype=float)
cl = np.array(close, dtype=float)
op = np.array(open, dtype=float)
n = len(cl)

vol_pct = np.zeros(n)
for i in range(length, n):
    window = vol[i-length:i]
    vol_pct[i] = np.sum(window <= vol[i]) / length * 100

high_vol = vol_pct > high_pct
bullish = cl > op

bull_high_vol = (high_vol & bullish)
bear_high_vol = (high_vol & ~bullish)
low_vol = vol_pct < 30

bgcolor(bull_high_vol.tolist(), color="rgba(76,175,80,0.15)")
bgcolor(bear_high_vol.tolist(), color="rgba(244,67,54,0.15)")
bgcolor(low_vol.tolist(), color="rgba(128,128,128,0.05)")

cooldown = 10
last = -cooldown
for i in range(length, n):
    if high_vol[i] and (i - last) >= cooldown:
        last = i
        if bullish[i]:
            label.new(x=i, y=float(cl[i]),
                      text=f"Vol {vol_pct[i]:.0f}%",
                      style=label.style_label_down, color="#4CAF50",
                      textcolor="#ffffff", size="tiny")
        else:
            label.new(x=i, y=float(cl[i]),
                      text=f"Vol {vol_pct[i]:.0f}%",
                      style=label.style_label_up, color="#f44336",
                      textcolor="#ffffff", size="tiny")
