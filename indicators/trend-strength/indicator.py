from tg_scripting import *

indicator("Trend Strength", overlay=False)

show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")
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

# --- Rich annotations ---
import numpy as np
n = len(close)
signal_line = ta.sma(score, 5)
last_strong_idx = -100
last_weak_idx = -100
last_cross_idx = -100
cooldown_bars = 20

for i in range(max(adx_len, aroon_len, vi_len) + 5, n):
    if show_labels and score[i] > strong_thresh and score[i - 1] <= strong_thresh and (i - last_strong_idx) > cooldown_bars:
        last_strong_idx = i
        label.new(
            x=i, y=float(score[i]),
            text="Strong Trend",
            style=label.style_label_down,
            color="rgba(0,230,118,0.25)",
            textcolor="#00e676",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=float(strong_thresh), x2=min(i + 20, n - 1), y2=float(strong_thresh),
                     color="#00e676", width=1, style=line.style_dotted)

    weak_thresh = 100 - strong_thresh
    if show_labels and score[i] < weak_thresh and score[i - 1] >= weak_thresh and (i - last_weak_idx) > cooldown_bars:
        last_weak_idx = i
        label.new(
            x=i, y=float(score[i]),
            text="Weak Trend",
            style=label.style_label_up,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )

    if show_labels and i > 1 and (i - last_cross_idx) > cooldown_bars:
        if score[i] > signal_line[i] and score[i - 1] <= signal_line[i - 1]:
            last_cross_idx = i
            label.new(
                x=i, y=float(score[i]),
                text="Strengthening",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="tiny"
            )
        elif score[i] < signal_line[i] and score[i - 1] >= signal_line[i - 1]:
            last_cross_idx = i
            label.new(
                x=i, y=float(score[i]),
                text="Weakening",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#888888",
                size="tiny"
            )
