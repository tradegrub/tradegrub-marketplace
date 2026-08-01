from tg_scripting import *

indicator("Volatility Regime", overlay=False)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
bb_len = input.int(20, "BB Length", minval=10, maxval=50)
bb_mult = input.float(2.0, "BB Multiplier", minval=1.0, maxval=4.0)
pct_len = input.int(100, "Percentile Lookback", minval=20, maxval=500)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

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

# --- Rich annotations ---
import numpy as np
n = len(close)
last_high_vol_idx = -100
last_low_vol_idx = -100
last_squeeze_idx = -100
cooldown_bars = 20

for i in range(pct_len + 1, n):
    if show_labels and vol_regime[i] > 80 and vol_regime[i - 1] <= 80 and (i - last_high_vol_idx) > cooldown_bars:
        last_high_vol_idx = i
        label.new(
            x=i, y=float(vol_regime[i]),
            text="High Volatility",
            style=label.style_label_down,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=80.0, x2=min(i + 20, n - 1), y2=80.0,
                     color="#ef5350", width=1, style=line.style_dotted)

    if show_labels and vol_regime[i] < 20 and vol_regime[i - 1] >= 20 and (i - last_low_vol_idx) > cooldown_bars:
        last_low_vol_idx = i
        label.new(
            x=i, y=float(vol_regime[i]),
            text="Squeeze",
            style=label.style_label_up,
            color="rgba(0,230,118,0.25)",
            textcolor="#00e676",
            size="small"
        )
        if show_levels:
            line.new(x1=i, y1=20.0, x2=min(i + 20, n - 1), y2=20.0,
                     color="#00e676", width=1, style=line.style_dotted)

    if show_labels and vol_regime[i] < 10 and (i - last_squeeze_idx) > cooldown_bars * 2:
        last_squeeze_idx = i
        label.new(
            x=i, y=float(vol_regime[i]),
            text="Compression",
            style=label.style_none,
            color="rgba(0,0,0,0)",
            textcolor="#42a5f5",
            size="tiny"
        )
