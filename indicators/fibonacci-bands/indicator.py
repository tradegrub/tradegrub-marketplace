from tg_scripting import *
import numpy as np

indicator("Fibonacci Bands", overlay=True)

length = input.int(50, "Lookback Length", minval=10, maxval=200)
show_fill = input.bool(True, "Show Fill Between Bands")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo

fib_236 = lo + rng * 0.236
fib_382 = lo + rng * 0.382
fib_500 = lo + rng * 0.500
fib_618 = lo + rng * 0.618
fib_786 = lo + rng * 0.786

p_hi = plot(hi, title="High", color="#B71C1C")
p_786 = plot(fib_786, title="Fib 78.6%", color="#EF5350")
p_618 = plot(fib_618, title="Fib 61.8%", color="#FF7043")
p_500 = plot(fib_500, title="Fib 50.0%", color="#FF9800")
p_382 = plot(fib_382, title="Fib 38.2%", color="#66BB6A")
p_236 = plot(fib_236, title="Fib 23.6%", color="#26A69A")
p_lo = plot(lo, title="Low", color="#004D40")

fill(p_618, p_382, color="rgba(255,152,0,0.08)")

# --- Rich annotations ---
n = len(close)
last_support_idx = -100
last_resist_idx = -100
last_mid_idx = -100
cooldown = 20

for i in range(length, n):
    if show_labels:
        # Price bouncing off 61.8% support
        if i > length and low[i] <= fib_618[i] and close[i] > fib_618[i] and close[i - 1] > fib_618[i - 1] and (i - last_support_idx) > cooldown:
            label.new(
                x=i, y=float(fib_618[i]),
                text="Fib 61.8% Support",
                style=label.style_label_up,
                color="rgba(0,230,118,0.2)",
                textcolor="#00e676",
                size="small"
            )
            last_support_idx = i

        # Price rejected at 61.8% resistance
        if i > length and high[i] >= fib_618[i] and close[i] < fib_618[i] and close[i - 1] < fib_618[i - 1] and (i - last_resist_idx) > cooldown:
            label.new(
                x=i, y=float(fib_618[i]),
                text="Fib 61.8% Resist",
                style=label.style_label_down,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_resist_idx = i

    if show_levels:
        # Price crossing the 50% midline
        if i > length and close[i] > fib_500[i] and close[i - 1] <= fib_500[i - 1] and (i - last_mid_idx) > cooldown:
            label.new(
                x=i, y=float(fib_500[i]),
                text="Above 50%",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="tiny"
            )
            last_mid_idx = i
        elif i > length and close[i] < fib_500[i] and close[i - 1] >= fib_500[i - 1] and (i - last_mid_idx) > cooldown:
            label.new(
                x=i, y=float(fib_500[i]),
                text="Below 50%",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#888888",
                size="tiny"
            )
            last_mid_idx = i
