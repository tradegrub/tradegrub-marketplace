from tg_scripting import *
import numpy as np

indicator("Correlation Indicator", overlay=False)

length = input.int(20, "Length", minval=5, maxval=200)
high_corr = input.float(0.7, "High Correlation", minval=0.3, maxval=1.0)
low_corr = input.float(-0.7, "Low Correlation", minval=-1.0, maxval=-0.3)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

corr = ta.correlation(close, volume, length)
corr_sma = ta.sma(corr, 5)

plot(corr, title="Correlation", color="#42A5F5")
plot(corr_sma, title="Signal", color="#FF7043")
h_hi = hline(high_corr, title="High Correlation", color="rgba(102,187,106,0.5)")
h_lo = hline(low_corr, title="Low Correlation", color="rgba(239,83,80,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")

bgcolor(corr > high_corr, color="rgba(102,187,106,0.06)")
bgcolor(corr < low_corr, color="rgba(239,83,80,0.06)")

# --- Rich annotations ---
n = len(close)
last_high_idx = -100
last_low_idx = -100
last_cross_idx = -100
cooldown = 20

for i in range(length, n):
    if show_labels:
        # High positive correlation zone entry
        if i > length and corr[i] > high_corr and corr[i - 1] <= high_corr and (i - last_high_idx) > cooldown:
            label.new(
                x=i, y=float(corr[i]),
                text="High Corr",
                style=label.style_label_down,
                color="rgba(102,187,106,0.2)",
                textcolor="#66bb6a",
                size="small"
            )
            last_high_idx = i

        # High negative correlation zone entry
        if i > length and corr[i] < low_corr and corr[i - 1] >= low_corr and (i - last_low_idx) > cooldown:
            label.new(
                x=i, y=float(corr[i]),
                text="Neg Corr",
                style=label.style_label_up,
                color="rgba(239,83,80,0.2)",
                textcolor="#ef5350",
                size="small"
            )
            last_low_idx = i

    if show_levels:
        # Signal line crossover
        if i > length and corr[i] > corr_sma[i] and corr[i - 1] <= corr_sma[i - 1] and (i - last_cross_idx) > cooldown:
            label.new(
                x=i, y=float(corr[i]),
                text="Cross Up",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="tiny"
            )
            last_cross_idx = i
