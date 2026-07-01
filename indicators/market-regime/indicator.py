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

indicator("Market Regime", overlay=False)

regime_score = np.where(trending, 1, np.where(ranging, -1, 0))

plot(adx_val, title="ADX", color="#42A5F5")
plot(chop_val, title="Choppiness", color="#FF7043")
hline(trend_thresh, title="Trend Threshold", color="rgba(66,165,245,0.5)")
hline(chop_thresh, title="Chop Threshold", color="rgba(255,112,67,0.5)")

bgcolor(trending, color="rgba(38,166,154,0.08)")
bgcolor(ranging, color="rgba(255,152,0,0.08)")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)
last_label_idx = -100
cooldown = 20

for i in range(1, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue
    # Regime transition labels
    if trending[i] and not trending[i - 1]:
        last_label_idx = i
        label.new(
            x=i, y=float(adx_val[i]),
            text="Trending",
            style=label.style_label_up,
            color="rgba(38,166,154,0.3)",
            textcolor="#26a69a",
            size="normal"
        )
    elif ranging[i] and not ranging[i - 1]:
        last_label_idx = i
        label.new(
            x=i, y=float(chop_val[i]),
            text="Ranging",
            style=label.style_label_down,
            color="rgba(255,152,0,0.3)",
            textcolor="#FF7043",
            size="normal"
        )
    elif not trending[i] and not ranging[i] and (trending[i - 1] or ranging[i - 1]):
        last_label_idx = i
        label.new(
            x=i, y=float(adx_val[i]),
            text="Transitional",
            style=label.style_none,
            color="rgba(0,0,0,0)",
            textcolor="#888888",
            size="small"
        )
