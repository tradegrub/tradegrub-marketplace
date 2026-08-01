from tg_scripting import *

indicator("Moving Avg Ribbon", overlay=True)

colors = [
    "rgba(244,67,54,0.9)",
    "rgba(255,87,34,0.9)",
    "rgba(255,152,0,0.9)",
    "rgba(255,193,7,0.9)",
    "rgba(205,220,57,0.9)",
    "rgba(139,195,74,0.9)",
    "rgba(76,175,80,0.9)",
    "rgba(0,150,136,0.9)",
    "rgba(0,188,212,0.9)",
    "rgba(33,150,243,0.9)",
]

sma10 = ta.sma(close, 10)
sma20 = ta.sma(close, 20)
sma30 = ta.sma(close, 30)
sma40 = ta.sma(close, 40)
sma50 = ta.sma(close, 50)
sma60 = ta.sma(close, 60)
sma70 = ta.sma(close, 70)
sma80 = ta.sma(close, 80)
sma90 = ta.sma(close, 90)
sma100 = ta.sma(close, 100)

p1 = plot(sma10, title="SMA 10", color=colors[0])
p2 = plot(sma20, title="SMA 20", color=colors[1])
p3 = plot(sma30, title="SMA 30", color=colors[2])
p4 = plot(sma40, title="SMA 40", color=colors[3])
p5 = plot(sma50, title="SMA 50", color=colors[4])
p6 = plot(sma60, title="SMA 60", color=colors[5])
p7 = plot(sma70, title="SMA 70", color=colors[6])
p8 = plot(sma80, title="SMA 80", color=colors[7])
p9 = plot(sma90, title="SMA 90", color=colors[8])
p10 = plot(sma100, title="SMA 100", color=colors[9])

fill(p1, p2, color="rgba(244,67,54,0.06)")
fill(p2, p3, color="rgba(255,87,34,0.06)")
fill(p3, p4, color="rgba(255,152,0,0.06)")
fill(p4, p5, color="rgba(255,193,7,0.06)")
fill(p5, p6, color="rgba(205,220,57,0.06)")
fill(p6, p7, color="rgba(139,195,74,0.06)")
fill(p7, p8, color="rgba(76,175,80,0.06)")
fill(p8, p9, color="rgba(0,150,136,0.06)")
fill(p9, p10, color="rgba(0,188,212,0.06)")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

import numpy as np

n = len(close)
last_label_idx = -100
cooldown = 30

sma_list = [sma10, sma20, sma30, sma40, sma50, sma60, sma70, sma80, sma90, sma100]

for i in range(100, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue

    # Check if all MAs are in bullish order (fast > slow)
    bullish_order = all(float(sma_list[k][i]) > float(sma_list[k + 1][i]) for k in range(9))
    bearish_order = all(float(sma_list[k][i]) < float(sma_list[k + 1][i]) for k in range(9))

    # Ribbon spread (distance between fastest and slowest)
    spread = abs(float(sma10[i]) - float(sma100[i]))
    avg_price = float(close[i])
    spread_pct = spread / avg_price * 100 if avg_price > 0 else 0

    if bullish_order and spread_pct > 1.0:
        last_label_idx = i
        label.new(
            x=i, y=float(sma10[i]),
            text="Bullish Ribbon",
            style=label.style_label_down,
            color="rgba(0,230,118,0.3)",
            textcolor="#00e676",
            size="small"
        )
    elif bearish_order and spread_pct > 1.0:
        last_label_idx = i
        label.new(
            x=i, y=float(sma10[i]),
            text="Bearish Ribbon",
            style=label.style_label_up,
            color="rgba(239,83,80,0.3)",
            textcolor="#ef5350",
            size="small"
        )

    # Detect ribbon compression (squeeze)
    if spread_pct < 0.3 and not bullish_order and not bearish_order:
        last_label_idx = i
        label.new(
            x=i, y=float(sma50[i]),
            text="Squeeze",
            style=label.style_none,
            color="rgba(0,0,0,0)",
            textcolor="#888888",
            size="small"
        )
