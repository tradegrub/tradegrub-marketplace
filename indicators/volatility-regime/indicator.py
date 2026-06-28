from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
bb_len = input.int(20, "BB Length", minval=10, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=1.0, maxval=4.0)
pct_len = input.int(100, "Percentile Lookback", minval=20, maxval=500)

atr_val = ta.atr(high, low, close, atr_len)
atr_pct = ta.percentrank(atr_val, pct_len)

bbw_val = ta.bbw(close, bb_len, bb_mult)
bbw_pct = ta.percentrank(bbw_val, pct_len)

vol_regime = (atr_pct + bbw_pct) / 2

plot(atr_pct, title="ATR Percentile", color="#42A5F5")
plot(bbw_pct, title="BBW Percentile", color="#FF7043")
plot(vol_regime, title="Volatility Regime", color="#AB47BC")

hline(80, title="High Volatility", color="rgba(239,83,80,0.5)")
hline(20, title="Low Volatility", color="rgba(38,166,154,0.5)")
hline(50, title="Neutral", color="rgba(128,128,128,0.3)")

bgcolor(vol_regime > 80, color="rgba(239,83,80,0.08)")
bgcolor(vol_regime < 20, color="rgba(38,166,154,0.08)")
