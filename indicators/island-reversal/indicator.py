from tg_scripting import *
import numpy as np

indicator("Island Reversal Detector", overlay=True)

gap_pct = input.float(0.5, "Min Gap %", minval=0.1, maxval=5.0, step=0.1)
island_len = input.int(5, "Max Island Bars", minval=2, maxval=20)
show_labels = input.bool(True, "Show Labels")

src_h = np.array(high, dtype=float)
src_l = np.array(low, dtype=float)
src_c = np.array(close, dtype=float)
src_o = np.array(open, dtype=float)
n = len(src_c)

bull_island = np.full(n, False)
bear_island = np.full(n, False)
island_top = np.full(n, np.nan)
island_bot = np.full(n, np.nan)

def has_gap_up(i):
    if i < 1:
        return False
    return src_l[i] > src_h[i - 1] * (1.0 + gap_pct / 100.0)

def has_gap_down(i):
    if i < 1:
        return False
    return src_h[i] < src_l[i - 1] * (1.0 - gap_pct / 100.0)

for i in range(2, n):
    if has_gap_down(i):
        for look in range(1, min(island_len + 1, i)):
            start = i - look
            if has_gap_up(start):
                zone_high = np.max(src_h[start:i])
                zone_low = np.min(src_l[start:i])
                bear_island[i] = True
                island_top[i] = zone_high
                island_bot[i] = zone_low
                break

    if has_gap_up(i):
        for look in range(1, min(island_len + 1, i)):
            start = i - look
            if has_gap_down(start):
                zone_high = np.max(src_h[start:i])
                zone_low = np.min(src_l[start:i])
                bull_island[i] = True
                island_top[i] = zone_high
                island_bot[i] = zone_low
                break

for i in range(n):
    if bear_island[i] and not np.isnan(island_top[i]):
        box.new(left=i - island_len, top=island_top[i], right=i,
                bottom=island_bot[i], border_color="rgba(239,83,80,0.5)",
                bgcolor="rgba(239,83,80,0.08)")
        if show_labels:
            label.new(x=i, y=src_h[i] * 1.005, text="Bear Island",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#FFFFFF", size="small")

    if bull_island[i] and not np.isnan(island_bot[i]):
        box.new(left=i - island_len, top=island_top[i], right=i,
                bottom=island_bot[i], border_color="rgba(76,175,80,0.5)",
                bgcolor="rgba(76,175,80,0.08)")
        if show_labels:
            label.new(x=i, y=src_l[i] * 0.995, text="Bull Island",
                      style=label.style_label_up, color="#4CAF50",
                      textcolor="#FFFFFF", size="small")

signal = np.where(bull_island, 1.0, np.where(bear_island, -1.0, 0.0))
plot(signal, title="Island Signal", color="#AB47BC", linewidth=1)
