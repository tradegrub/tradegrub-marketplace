from tg_scripting import *
import numpy as np

indicator("EMA Ribbon", overlay=True)

show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

ema8 = ta.ema(close, 8)
ema13 = ta.ema(close, 13)
ema21 = ta.ema(close, 21)
ema34 = ta.ema(close, 34)
ema55 = ta.ema(close, 55)
ema89 = ta.ema(close, 89)

p1 = plot(ema8, title="EMA 8", color="rgba(0,188,212,0.9)")
p2 = plot(ema13, title="EMA 13", color="rgba(0,150,136,0.9)")
p3 = plot(ema21, title="EMA 21", color="rgba(76,175,80,0.9)")
p4 = plot(ema34, title="EMA 34", color="rgba(255,193,7,0.9)")
p5 = plot(ema55, title="EMA 55", color="rgba(255,87,34,0.9)")
p6 = plot(ema89, title="EMA 89", color="rgba(244,67,54,0.9)")

fill(p1, p2, color="rgba(0,188,212,0.08)")
fill(p2, p3, color="rgba(0,150,136,0.08)")
fill(p3, p4, color="rgba(76,175,80,0.08)")
fill(p4, p5, color="rgba(255,193,7,0.08)")
fill(p5, p6, color="rgba(255,87,34,0.08)")

# --- Rich annotations ---
n = len(close)
last_bull_idx = -100
last_bear_idx = -100
last_spread_idx = -100
cooldown = 20

for i in range(89, n):
    # All EMAs aligned bullish: 8 > 13 > 21 > 34 > 55 > 89
    all_bull = (ema8[i] > ema13[i] > ema21[i] > ema34[i] > ema55[i] > ema89[i])
    all_bear = (ema8[i] < ema13[i] < ema21[i] < ema34[i] < ema55[i] < ema89[i])

    if show_labels:
        # Bullish alignment
        if all_bull and not (ema8[i - 1] > ema13[i - 1] > ema21[i - 1] > ema34[i - 1] > ema55[i - 1] > ema89[i - 1]) and (i - last_bull_idx) > cooldown:
            label.new(
                x=i, y=float(low[i]),
                text="Bull Ribbon",
                style=label.style_label_up,
                color="rgba(0,230,118,0.2)",
                textcolor="#00e676",
                size="small"
            )
            last_bull_idx = i

        # Bearish alignment
        if all_bear and not (ema8[i - 1] < ema13[i - 1] < ema21[i - 1] < ema34[i - 1] < ema55[i - 1] < ema89[i - 1]) and (i - last_bear_idx) > cooldown:
            label.new(
                x=i, y=float(high[i]),
                text="Bear Ribbon",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_bear_idx = i

    if show_levels:
        # Ribbon squeeze: fast and slow EMAs converging
        spread = float(abs(ema8[i] - ema89[i]))
        avg_price = float(close[i])
        if avg_price > 0 and (spread / avg_price) < 0.005 and (i - last_spread_idx) > cooldown:
            label.new(
                x=i, y=float(ema55[i]),
                text="Squeeze",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="small"
            )
            last_spread_idx = i
