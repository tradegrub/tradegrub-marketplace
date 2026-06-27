from tg_scripting import *

lookback = input.int("Lookback Bars", 100, minval=10, maxval=500)
rows = input.int("Row Count", 24, minval=10, maxval=100)
va_pct = input.float("Value Area %", 70.0, minval=50.0, maxval=90.0)

price_high = ta.highest(high, lookback)
price_low = ta.lowest(low, lookback)
row_height = (price_high - price_low) / rows

vol_bins = [0.0] * rows
for i in range(lookback):
    bar_mid = (high[i] + low[i]) / 2
    bin_idx = int((bar_mid - price_low) / row_height)
    bin_idx = min(bin_idx, rows - 1)
    vol_bins[bin_idx] += volume[i]

poc_idx = vol_bins.index(max(vol_bins))
poc_price = price_low + (poc_idx + 0.5) * row_height

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

vah = price_low + (hi_idx + 1) * row_height
val_price = price_low + lo_idx * row_height

hline(poc_price, "POC", color="orange", linewidth=2)
hline(vah, "VAH", color="rgba(38,166,154,0.6)", linestyle="dashed")
hline(val_price, "VAL", color="rgba(239,83,80,0.6)", linestyle="dashed")
