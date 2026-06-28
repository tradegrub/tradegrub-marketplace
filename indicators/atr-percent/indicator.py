from tg_scripting import *

length = input.int(14, "ATR Length", minval=1, maxval=100)
smooth = input.int(5, "Smoothing", minval=1, maxval=20)

atr_val = ta.atr(high, low, close, length)
atr_pct = (atr_val / close) * 100
atr_pct_smooth = ta.sma(atr_pct, smooth)

plot(atr_pct, title="ATR %", color="#AB47BC")
plot(atr_pct_smooth, title="Smoothed", color="#FF7043")
