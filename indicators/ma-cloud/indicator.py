from tg_scripting import *
import numpy as np

indicator("MA Cloud", overlay=True)

show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

fast_len = input.int(20, "Fast MA Length", minval=1, maxval=200)
slow_len = input.int(50, "Slow MA Length", minval=2, maxval=500)
ma_type = input.string("SMA", "MA Type", options=["SMA", "EMA"])

if ma_type == "SMA":
    fast_ma = ta.sma(close, fast_len)
    slow_ma = ta.sma(close, slow_len)
else:
    fast_ma = ta.ema(close, fast_len)
    slow_ma = ta.ema(close, slow_len)

bullish = fast_ma > slow_ma

p1 = plot(fast_ma, title="Fast MA", color="rgba(38,166,154,1)")
p2 = plot(slow_ma, title="Slow MA", color="rgba(239,83,80,1)")

fill_color = np.where(bullish, "rgba(38,166,154,0.15)", "rgba(239,83,80,0.15)")
fill(p1, p2, color=fill_color)

# --- Rich annotations ---
n = len(close)
last_golden_idx = -100
last_death_idx = -100
cooldown = 20

for i in range(slow_len, n):
    if show_labels:
        # Golden cross: fast crosses above slow
        if fast_ma[i] > slow_ma[i] and fast_ma[i - 1] <= slow_ma[i - 1] and (i - last_golden_idx) > cooldown:
            label.new(
                x=i, y=float(low[i]),
                text="Golden Cross",
                style=label.style_label_up,
                color="rgba(0,230,118,0.3)",
                textcolor="#00e676",
                size="normal"
            )
            last_golden_idx = i

        # Death cross: fast crosses below slow
        if fast_ma[i] < slow_ma[i] and fast_ma[i - 1] >= slow_ma[i - 1] and (i - last_death_idx) > cooldown:
            label.new(
                x=i, y=float(high[i]),
                text="Death Cross",
                style=label.style_label_down,
                color="rgba(239,83,80,0.3)",
                textcolor="#ef5350",
                size="normal"
            )
            last_death_idx = i

    if show_levels:
        # Draw crossover point line
        if fast_ma[i] > slow_ma[i] and fast_ma[i - 1] <= slow_ma[i - 1] and (i - last_golden_idx) == 0:
            cross_price = float((fast_ma[i] + slow_ma[i]) / 2)
            line.new(
                x1=i, y1=cross_price,
                x2=min(i + 10, n - 1), y2=cross_price,
                color="#00e676", width=1, style=line.style_dashed
            )
        if fast_ma[i] < slow_ma[i] and fast_ma[i - 1] >= slow_ma[i - 1] and (i - last_death_idx) == 0:
            cross_price = float((fast_ma[i] + slow_ma[i]) / 2)
            line.new(
                x1=i, y1=cross_price,
                x2=min(i + 10, n - 1), y2=cross_price,
                color="#ef5350", width=1, style=line.style_dashed
            )
