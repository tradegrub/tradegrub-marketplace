from tg_scripting import *

adx_len = input.int(14, "ADX Length", minval=5, maxval=50)
aroon_len = input.int(25, "Aroon Length", minval=10, maxval=50)
vi_len = input.int(14, "Vortex Length", minval=5, maxval=50)
strong_thresh = input.int(70, "Strong Trend", minval=50, maxval=90)

adx_val = ta.adx(high, low, close, adx_len, adx_len)
aroon_up, aroon_down = ta.aroon(high, low, aroon_len)
vi_plus, vi_minus = ta.vi(high, low, close, vi_len)

adx_norm = adx_val / 50 * 100
aroon_diff = aroon_up - aroon_down
aroon_norm = (aroon_diff + 100) / 2
vi_diff = vi_plus - vi_minus
vi_norm = (vi_diff + 1) / 2 * 100

score = (adx_norm + aroon_norm + vi_norm) / 3

plot(score, title="Trend Strength", color="#7E57C2")
plot(ta.sma(score, 5), title="Signal", color="#FF8A65")
hline(strong_thresh, title="Strong Trend", color="rgba(126,87,194,0.5)")
hline(50, title="Neutral", color="rgba(128,128,128,0.3)")
hline(100 - strong_thresh, title="Weak Trend", color="rgba(255,138,101,0.5)")

bgcolor(score > strong_thresh, color="rgba(38,166,154,0.06)")
bgcolor(score < 100 - strong_thresh, color="rgba(239,83,80,0.06)")
