from tg_scripting import *
import numpy as np

indicator("Institutional Candle Profile", overlay=True)

vol_mult = input.float(2.0, "Volume Multiplier", minval=1.0, maxval=5.0, step=0.1)
vol_len = input.int(20, "Volume MA Length", minval=5, maxval=100)
body_pct = input.float(0.6, "Min Body Percent", minval=0.3, maxval=0.9, step=0.05)
show_labels = input.bool(True, "Show Labels")

n = len(close)
vol_ma = ta.sma(volume, vol_len)
atr = ta.atr(high, low, close, 14)

body = np.abs(np.array(close) - np.array(open))
total_range = np.array(high) - np.array(low) + 1e-10
body_ratio = body / total_range

high_vol = np.array(volume) > (np.array(vol_ma) * vol_mult)
large_body = body_ratio >= body_pct

bullish_inst = high_vol & large_body & (np.array(close) > np.array(open))
bearish_inst = high_vol & large_body & (np.array(close) < np.array(open))

# Absorption: high volume but small body (large wicks)
small_body = body_ratio < 0.3
absorption = high_vol & small_body

plotshape(bullish_inst, title="Bull Institutional", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bearish_inst, title="Bear Institutional", shape="triangledown", location="abovebar", color="#ff1744", size="small")
plotshape(absorption, title="Absorption", shape="diamond", location="abovebar", color="#ffab00", size="tiny")

bgcolor(absorption, color="rgba(255,171,0,0.05)")

# Volume ratio subplot
vol_ratio = np.where(vol_ma > 0, np.array(volume) / np.array(vol_ma), 1.0)
plot(vol_ratio, title="Volume Ratio", color="#42A5F5", display="none")

if show_labels:
    last_lbl = -15
    for i in range(vol_len, n):
        if i - last_lbl < 15:
            continue
        if bullish_inst[i]:
            label.new(x=i, y=float(low[i]), text="Inst Buy",
                      style=label.style_label_up, color="rgba(0,230,118,0.4)",
                      textcolor="#00e676", size="tiny")
            last_lbl = i
        elif bearish_inst[i]:
            label.new(x=i, y=float(high[i]), text="Inst Sell",
                      style=label.style_label_down, color="rgba(255,23,68,0.4)",
                      textcolor="#ff1744", size="tiny")
            last_lbl = i
        elif absorption[i]:
            label.new(x=i, y=float(high[i]), text="Absorb",
                      style=label.style_label_down, color="rgba(255,171,0,0.4)",
                      textcolor="#ffab00", size="tiny")
            last_lbl = i
