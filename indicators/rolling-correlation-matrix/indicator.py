from tg_scripting import *
import numpy as np
import pandas as pd

indicator("Rolling Correlation Matrix", overlay=False)

corr_window = input.int(30, "Correlation Window", minval=10, maxval=100)
z_threshold = input.float(2.0, "Divergence Z-Score", minval=1.0, maxval=3.0)
smooth = input.int(5, "Smoothing", minval=1, maxval=20)
show_divergence = input.bool(True, "Show Divergence Alerts")

df = pd.DataFrame({'close': close, 'volume': volume, 'high': high, 'low': low})

df['returns'] = df['close'].pct_change()
df['log_vol'] = np.log1p(df['volume'])
df['range_pct'] = (df['high'] - df['low']) / df['close']
df['body_pct'] = np.abs(df['close'] - open) / df['close']

price_vol_corr = df['returns'].rolling(corr_window).corr(df['log_vol'])
price_range_corr = df['returns'].rolling(corr_window).corr(df['range_pct'])
vol_range_corr = df['log_vol'].rolling(corr_window).corr(df['range_pct'])

avg_corr = (price_vol_corr + price_range_corr + vol_range_corr) / 3
avg_smooth = avg_corr.rolling(smooth).mean()

valid_block = avg_smooth.dropna()
if len(valid_block) > 20:
    z_vals = pd.Series(np.nan, index=avg_smooth.index)
    z_vals[valid_block.index] = (valid_block.values - np.mean(valid_block.values)) / np.std(valid_block.values)
else:
    z_vals = pd.Series(0.0, index=avg_smooth.index)

divergence_high = z_vals > z_threshold
divergence_low = z_vals < -z_threshold

plot(price_vol_corr.to_numpy(), title="Price-Volume Corr", color="#2196f3")
plot(price_range_corr.to_numpy(), title="Price-Range Corr", color="#ff9800")
plot(avg_smooth.to_numpy(), title="Average Correlation", color="white", linewidth=2)
hline(0, title="Zero", color="gray")

if show_divergence:
    plotshape(divergence_high.to_numpy(), title="High Correlation", shape="diamond", location="abovebar", color="#00e676", size="tiny")
    plotshape(divergence_low.to_numpy(), title="Low Correlation", shape="diamond", location="belowbar", color="#ff1744", size="tiny")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

n = len(close)
last_label_idx = -100
cooldown = 20
dh_arr = divergence_high.to_numpy()
dl_arr = divergence_low.to_numpy()
avg_arr = avg_smooth.to_numpy()
pv_arr = price_vol_corr.to_numpy()

for i in range(corr_window + smooth, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue

    if dh_arr[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(avg_arr[i]) if not np.isnan(avg_arr[i]) else 0.0,
            text="High Correlation",
            style=label.style_label_down,
            color="rgba(0,230,118,0.3)",
            textcolor="#00e676",
            size="small"
        )
    elif dl_arr[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(avg_arr[i]) if not np.isnan(avg_arr[i]) else 0.0,
            text="Divergence",
            style=label.style_label_up,
            color="rgba(255,23,68,0.3)",
            textcolor="#ff1744",
            size="small"
        )

    # Label zero-crossing of average correlation
    if show_levels and i > 0:
        a_cur = avg_arr[i] if not np.isnan(avg_arr[i]) else 0.0
        a_prev = avg_arr[i - 1] if not np.isnan(avg_arr[i - 1]) else 0.0
        if a_cur > 0 and a_prev <= 0 and (i - last_label_idx) > cooldown:
            last_label_idx = i
            label.new(
                x=i, y=float(a_cur),
                text="Positive Corr",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#42a5f5",
                size="tiny"
            )
        elif a_cur < 0 and a_prev >= 0 and (i - last_label_idx) > cooldown:
            last_label_idx = i
            label.new(
                x=i, y=float(a_cur),
                text="Negative Corr",
                style=label.style_none,
                color="rgba(0,0,0,0)",
                textcolor="#888888",
                size="tiny"
            )
