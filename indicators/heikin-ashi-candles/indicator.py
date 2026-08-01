from tg_scripting import *
import numpy as np

indicator("Heikin Ashi Candles", overlay=True)

show_real = input.bool(False, "Show Real Candles Too")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

ha_close = (open + high + low + close) / 4
ha_open = ta.sma((open + close) / 2, 2)
ha_high = ta.highest(high, 1)
ha_low = ta.lowest(low, 1)

plotcandle(ha_open, ha_high, ha_low, ha_close, title="Heikin-Ashi")

# --- Rich annotations ---
n = len(close)
ha_bull = ha_close > ha_open
ha_bear = ha_close < ha_open

last_reversal_idx = -100
last_doji_idx = -100
cooldown = 15

for i in range(2, n):
    if show_labels:
        # HA trend reversal: bear to bull
        if ha_bull[i] and ha_bear[i - 1] and ha_bear[i - 2] and (i - last_reversal_idx) > cooldown:
            label.new(
                x=i, y=float(low[i]),
                text="HA Bull Flip",
                style=label.style_label_up,
                color="rgba(0,230,118,0.2)",
                textcolor="#00e676",
                size="small"
            )
            last_reversal_idx = i

        # HA trend reversal: bull to bear
        if ha_bear[i] and ha_bull[i - 1] and ha_bull[i - 2] and (i - last_reversal_idx) > cooldown:
            label.new(
                x=i, y=float(high[i]),
                text="HA Bear Flip",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_reversal_idx = i

    if show_levels:
        # HA Doji: very small body relative to range
        ha_body = abs(float(ha_close[i]) - float(ha_open[i]))
        ha_range = float(ha_high[i]) - float(ha_low[i])
        if ha_range > 0 and ha_body / ha_range < 0.1 and (i - last_doji_idx) > cooldown:
            label.new(
                x=i, y=float(ha_high[i]),
                text="HA Doji",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#888888",
                size="tiny"
            )
            last_doji_idx = i
