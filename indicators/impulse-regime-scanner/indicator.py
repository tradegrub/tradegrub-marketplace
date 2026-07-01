from tg_scripting import *
import numpy as np

indicator("Impulse Regime Scanner", overlay=False)

consol_len = input.int(20, "Consolidation Window", minval=10, maxval=60)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
impulse_mult = input.float(2.0, "Impulse Threshold", minval=1.0, maxval=4.0, step=0.25)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

range_pct = np.zeros(n)
for i in range(consol_len, n):
    period_range = np.max(hi[i-consol_len:i+1]) - np.min(lo[i-consol_len:i+1])
    range_pct[i] = period_range / max(cl[i], 1e-10) * 100

avg_atr_pct = np.zeros(n)
for i in range(consol_len, n):
    avg_atr_pct[i] = np.mean(atr_arr[i-consol_len:i]) / max(cl[i], 1e-10) * 100

consol_score = np.zeros(n)
for i in range(consol_len, n):
    expected = avg_atr_pct[i] * consol_len * 0.4
    if expected > 0:
        consol_score[i] = (1 - min(range_pct[i] / expected, 2) / 2) * 100

bar_range = np.abs(cl - np.array(open, dtype=float))
impulse = np.zeros(n)
for i in range(atr_len, n):
    if atr_arr[i] > 0:
        impulse[i] = bar_range[i] / atr_arr[i]

impulse_fired = impulse > impulse_mult

regime = np.zeros(n)
for i in range(consol_len, n):
    if impulse_fired[i]:
        regime[i] = 2  # Impulse breakout
    elif consol_score[i] > 70:
        regime[i] = 0  # Consolidation
    else:
        regime[i] = 1  # Trending

consolidating = regime == 0
trending = regime == 1
impulse_bar = regime == 2

plot(consol_score.tolist(), title="Consolidation Score", color="#ab47bc", linewidth=2)
plot((impulse * 30).tolist(), title="Impulse Strength", color="#ff9800", linewidth=1)
hline(70, title="Consolidation Zone", color="#42a5f5", linestyle="dashed")
hline(impulse_mult * 30, title="Impulse Threshold", color="#f44336", linestyle="dashed")
bgcolor(consolidating.tolist(), color="rgba(66,165,245,0.08)")
bgcolor(impulse_bar.tolist(), color="rgba(255,152,0,0.15)")

cooldown = 10
last = -cooldown
for i in range(consol_len, n):
    if impulse_fired[i] and (i - last) >= cooldown:
        last = i
        direction = "BULL" if cl[i] > float(open[i]) else "BEAR"
        color = "#4CAF50" if cl[i] > float(open[i]) else "#f44336"
        label.new(x=i, y=float(impulse[i] * 30),
                  text=f"Impulse {direction}",
                  style=label.style_label_down, color=color,
                  textcolor="#ffffff", size="tiny")
