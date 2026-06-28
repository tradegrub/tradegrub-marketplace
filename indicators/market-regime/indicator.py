from tg_scripting import *

adx_len = input.int(14, "ADX Length", minval=5, maxval=50)
chop_len = input.int(14, "Choppiness Length", minval=5, maxval=50)
trend_thresh = input.int(25, "Trend Threshold", minval=15, maxval=40)
chop_thresh = input.float(61.8, "Chop Threshold", minval=50.0, maxval=75.0)

adx_val = ta.adx(high, low, close, adx_len, adx_len)
chop_val = ta.chop(high, low, close, chop_len)

trending = (adx_val > trend_thresh) & (chop_val < chop_thresh)
ranging = (adx_val < trend_thresh) & (chop_val > chop_thresh)

import numpy as np
regime_score = np.where(trending, 1, np.where(ranging, -1, 0))

plot(adx_val, title="ADX", color="#42A5F5")
plot(chop_val, title="Choppiness", color="#FF7043")
hline(trend_thresh, title="Trend Threshold", color="rgba(66,165,245,0.5)")
hline(chop_thresh, title="Chop Threshold", color="rgba(255,112,67,0.5)")

bgcolor(trending, color="rgba(38,166,154,0.08)")
bgcolor(ranging, color="rgba(255,152,0,0.08)")
