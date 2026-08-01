from tg_scripting import *

indicator("Volume Profile Poc", overlay=True)

lookback = input.int(100, "Lookback Bars", minval=10, maxval=500)
rows = input.int(24, "Row Count", minval=10, maxval=100)
va_pct = input.float(70.0, "Value Area %", minval=50.0, maxval=90.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

price_high_val = float(ta.highest(high, lookback)[-1])
price_low_val = float(ta.lowest(low, lookback)[-1])
row_height = (price_high_val - price_low_val) / rows

vol_bins = [0.0] * rows
for i in range(lookback):
    bar_mid = (high[i] + low[i]) / 2
    bin_idx = int((bar_mid - price_low_val) / row_height)
    bin_idx = min(bin_idx, rows - 1)
    vol_bins[bin_idx] += volume[i]

poc_idx = vol_bins.index(max(vol_bins))
poc_price = price_low_val + (poc_idx + 0.5) * row_height

total_vol = sum(vol_bins)
target_vol = total_vol * (va_pct / 100)
cum_vol = vol_bins[poc_idx]
lo_idx = poc_idx
hi_idx = poc_idx
while cum_vol < target_vol:
    expand_lo = vol_bins[lo_idx - 1] if lo_idx > 0 else 0
    expand_hi = vol_bins[hi_idx + 1] if hi_idx < rows - 1 else 0
    if expand_lo >= expand_hi and lo_idx > 0:
        lo_idx -= 1
        cum_vol += vol_bins[lo_idx]
    elif hi_idx < rows - 1:
        hi_idx += 1
        cum_vol += vol_bins[hi_idx]
    else:
        break

vah = price_low_val + (hi_idx + 1) * row_height
val_price = price_low_val + lo_idx * row_height

hline(poc_price, title="POC", color="orange", linewidth=2)
hline(vah, title="VAH", color="rgba(38,166,154,0.6)", linestyle="dashed")
hline(val_price, title="VAL", color="rgba(239,83,80,0.6)", linestyle="dashed")

# --- Rich annotations ---
import numpy as np
n = len(close)
last_poc_label_idx = -100
last_vah_label_idx = -100
last_val_label_idx = -100
cooldown_bars = lookback // 2

for i in range(lookback, n):
    # Label POC touch/bounce
    if show_labels and abs(float(close[i]) - poc_price) < row_height and (i - last_poc_label_idx) > cooldown_bars:
        last_poc_label_idx = i
        label.new(
            x=i, y=poc_price,
            text="POC",
            style=label.style_label_left,
            color="rgba(255,152,0,0.25)",
            textcolor="#FF9800",
            size="small"
        )

    # Label VAH test
    if show_labels and float(high[i]) >= vah and float(high[i - 1]) < vah and (i - last_vah_label_idx) > cooldown_bars:
        last_vah_label_idx = i
        label.new(
            x=i, y=vah,
            text="VAH Test",
            style=label.style_label_down,
            color="rgba(38,166,154,0.25)",
            textcolor="#26a69a",
            size="small"
        )

    # Label VAL test
    if show_labels and float(low[i]) <= val_price and float(low[i - 1]) > val_price and (i - last_val_label_idx) > cooldown_bars:
        last_val_label_idx = i
        label.new(
            x=i, y=val_price,
            text="VAL Test",
            style=label.style_label_up,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )

# Value area box at the end of chart
if show_levels and n > lookback:
    box.new(left=n - lookback, top=vah, right=n - 1, bottom=val_price,
            border_color="rgba(255,152,0,0.2)", bgcolor="rgba(255,152,0,0.03)")
