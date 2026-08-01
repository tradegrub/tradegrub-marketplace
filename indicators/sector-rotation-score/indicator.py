from tg_scripting import *
import numpy as np

indicator("Sector Rotation Score", overlay=False)

rs_length = input.int(14, "RS Length", minval=5, maxval=50)
mom_length = input.int(10, "Momentum Length", minval=3, maxval=30)
smooth = input.int(5, "Smoothing", minval=1, maxval=20)
bench_length = input.int(20, "Benchmark Period", minval=5, maxval=100)
upper_threshold = input.float(1.05, "Strong Threshold", minval=1.0, maxval=2.0)
lower_threshold = input.float(0.95, "Weak Threshold", minval=0.5, maxval=1.0)
show_fill = input.bool(True, "Show Background Fill")
show_quadrant = input.bool(True, "Show Quadrant Labels")

benchmark = ta.sma(close, bench_length)
rs_ratio = close / benchmark
rs_smooth = ta.sma(rs_ratio, smooth)
rs_momentum = ta.change(rs_smooth, mom_length)
mom_smooth = ta.sma(rs_momentum, smooth)

score = (rs_smooth - 1.0) * 50 + mom_smooth * 500
score_final = ta.sma(score, smooth)

rising_rs = rs_smooth > np.concatenate([np.full(1, np.nan), (rs_smooth)[:-1]])
rising_mom = mom_smooth > np.concatenate([np.full(1, np.nan), (mom_smooth)[:-1]])

leading = rising_rs & rising_mom
weakening = rising_rs & ~rising_mom
lagging = ~rising_rs & ~rising_mom
improving = ~rising_rs & rising_mom

plot(score_final, title="Rotation Score", color="blue", linewidth=2)
hline(0, title="Zero Line", color="gray", linestyle="dashed")
hline(5, title="Strong", color="green", linestyle="dotted")
hline(-5, title="Weak", color="red", linestyle="dotted")

if show_fill:
    bgcolor(leading, color="rgba(0,200,0,0.08)")
    bgcolor(lagging, color="rgba(200,0,0,0.08)")
    bgcolor(improving, color="rgba(0,100,200,0.08)")
    bgcolor(weakening, color="rgba(200,200,0,0.08)")

if show_quadrant:
    plotshape(ta.crossover(score_final, 5), style="triangleup", location="belowbar", color="green", size="small")
    plotshape(ta.crossunder(score_final, -5), style="triangledown", location="abovebar", color="red", size="small")

plot(rs_smooth * 10 - 10, title="RS Ratio (scaled)", color="orange", linewidth=1)
plot(mom_smooth * 100, title="Momentum (scaled)", color="purple", linewidth=1)

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

cross_strong = ta.crossover(score_final, 5)
cross_weak = ta.crossunder(score_final, -5)

n = len(close)
last_label_idx = -100
cooldown = 20

for i in range(smooth + mom_length, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue

    if cross_strong[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(score_final[i]),
            text="Strong Rotation",
            style=label.style_label_up,
            color="rgba(0,200,0,0.3)",
            textcolor="#00e676",
            size="small"
        )
    elif cross_weak[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(score_final[i]),
            text="Weak Rotation",
            style=label.style_label_down,
            color="rgba(239,83,80,0.3)",
            textcolor="#ef5350",
            size="small"
        )

    # Quadrant labels
    if show_levels:
        if leading[i] and (i == 0 or not leading[i - 1]):
            if (i - last_label_idx) > cooldown // 2:
                last_label_idx = i
                label.new(
                    x=i, y=float(score_final[i]),
                    text="Leading",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#00c853",
                    size="tiny"
                )
        elif lagging[i] and (i == 0 or not lagging[i - 1]):
            if (i - last_label_idx) > cooldown // 2:
                last_label_idx = i
                label.new(
                    x=i, y=float(score_final[i]),
                    text="Lagging",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#ef5350",
                    size="tiny"
                )
        elif improving[i] and (i == 0 or not improving[i - 1]):
            if (i - last_label_idx) > cooldown // 2:
                last_label_idx = i
                label.new(
                    x=i, y=float(score_final[i]),
                    text="Improving",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#42a5f5",
                    size="tiny"
                )
        elif weakening[i] and (i == 0 or not weakening[i - 1]):
            if (i - last_label_idx) > cooldown // 2:
                last_label_idx = i
                label.new(
                    x=i, y=float(score_final[i]),
                    text="Weakening",
                    style=label.style_none,
                    color="rgba(0,0,0,0)",
                    textcolor="#FFD600",
                    size="tiny"
                )
