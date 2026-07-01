from tg_scripting import *

indicator("MA Crossover Signal", overlay=True)

fast_len = input.int(9, "Fast MA Length", minval=1, maxval=100)
slow_len = input.int(21, "Slow MA Length", minval=2, maxval=300)
ma_type = input.string("EMA", "MA Type", options=["SMA", "EMA", "WMA", "HMA"])

if ma_type == "SMA":
    fast_ma = ta.sma(close, fast_len)
    slow_ma = ta.sma(close, slow_len)
elif ma_type == "EMA":
    fast_ma = ta.ema(close, fast_len)
    slow_ma = ta.ema(close, slow_len)
elif ma_type == "WMA":
    fast_ma = ta.wma(close, fast_len)
    slow_ma = ta.wma(close, slow_len)
else:
    fast_ma = ta.hma(close, fast_len)
    slow_ma = ta.hma(close, slow_len)

cross_up = ta.crossover(fast_ma, slow_ma)
cross_down = ta.crossunder(fast_ma, slow_ma)

plot(fast_ma, title="Fast MA", color="rgba(38,166,154,1)")
plot(slow_ma, title="Slow MA", color="rgba(239,83,80,1)")

plotshape(cross_up, title="Bullish Cross", style="triangleup", location="belowbar", color="green", size="small")
plotshape(cross_down, title="Bearish Cross", style="triangledown", location="abovebar", color="red", size="small")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

import numpy as np

n = len(close)
last_signal_idx = -100
cooldown = max(slow_len, 20)

for i in range(slow_len, n):
    if show_labels and cross_up[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        label.new(
            x=i, y=float(low[i]),
            text="Golden Cross",
            style=label.style_label_up,
            color="#00e676",
            textcolor="#000000",
            size="normal"
        )
        if show_levels:
            label.new(
                x=i + 2, y=float(fast_ma[i]),
                text="Fast MA",
                style=label.style_label_left,
                color="rgba(38,166,154,0.2)",
                textcolor="#26a69a",
                size="small"
            )
    elif show_labels and cross_down[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        label.new(
            x=i, y=float(high[i]),
            text="Death Cross",
            style=label.style_label_down,
            color="#ef5350",
            textcolor="#ffffff",
            size="normal"
        )
        if show_levels:
            label.new(
                x=i + 2, y=float(fast_ma[i]),
                text="Fast MA",
                style=label.style_label_left,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
