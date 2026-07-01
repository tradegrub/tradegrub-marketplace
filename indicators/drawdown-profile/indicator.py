from tg_scripting import *
import numpy as np

indicator("Drawdown Profile Analysis", overlay=False)

lookback = input.int(50, "Rolling Window", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")
label_cooldown = input.int(20, "Label Cooldown Bars", minval=5, maxval=50)

close_arr = np.array(close, dtype=np.float64)
n = len(close_arr)

# Rolling max and drawdown
running_max = np.full(n, np.nan)
drawdown_pct = np.full(n, np.nan)
drawdown_duration = np.full(n, np.nan)
recovery_time = np.full(n, np.nan)
max_drawdown_rolling = np.full(n, np.nan)

# Compute running max and drawdown
peak = close_arr[0]
dur_count = 0
for i in range(n):
    if close_arr[i] > peak:
        peak = close_arr[i]
        dur_count = 0
    dd = (close_arr[i] / peak - 1.0) * 100.0
    drawdown_pct[i] = dd
    if dd < -0.01:
        dur_count += 1
    else:
        dur_count = 0
    drawdown_duration[i] = float(dur_count)

# Rolling max drawdown
for i in range(lookback, n):
    window = drawdown_pct[i - lookback:i + 1]
    max_drawdown_rolling[i] = float(np.nanmin(window))

# Recovery time: bars since last peak
bars_since_peak = np.zeros(n)
count = 0
for i in range(n):
    if drawdown_pct[i] >= -0.01:
        count = 0
    else:
        count += 1
    bars_since_peak[i] = float(count)

# Recovery zones: identify where drawdown ends (crosses back above -0.1%)
recovery_mask = np.zeros(n, dtype=bool)
for i in range(1, n):
    if drawdown_pct[i] >= -0.01 and drawdown_pct[i-1] < -0.5:
        recovery_mask[i] = True

# Plots
plot(drawdown_pct, title="Drawdown %", color="#ef5350")
plot(max_drawdown_rolling, title="Rolling Max DD", color="#FF7043")
plot(drawdown_duration, title="DD Duration", color="#AB47BC")

if show_levels:
    hline(0.0, title="Zero Line", color="rgba(255,255,255,0.3)")
    hline(-5.0, title="-5% Level", color="rgba(255,152,0,0.4)")
    hline(-10.0, title="-10% Level", color="rgba(239,83,80,0.4)")
    hline(-20.0, title="-20% Level", color="rgba(183,28,28,0.5)")

# Color zones
mild_dd = (drawdown_pct < -1.0) & (drawdown_pct >= -5.0)
moderate_dd = (drawdown_pct < -5.0) & (drawdown_pct >= -10.0)
severe_dd = drawdown_pct < -10.0

bgcolor(mild_dd, color="rgba(255,152,0,0.05)")
bgcolor(moderate_dd, color="rgba(239,83,80,0.08)")
bgcolor(severe_dd, color="rgba(183,28,28,0.12)")

if show_labels:
    last_label = -label_cooldown
    for i in range(1, n):
        if recovery_mask[i] and (i - last_label) > label_cooldown:
            label.new(
                x=i, y=0.0,
                text=f"Recovery\n{int(bars_since_peak[i-1])} bars",
                style=label.style_label_down,
                color="rgba(76,175,80,0.3)",
                textcolor="#4CAF50",
                size="small"
            )
            last_label = i

    # Mark deepest drawdown
    if n > lookback:
        worst_idx = int(np.nanargmin(drawdown_pct[lookback:])) + lookback
        worst_val = drawdown_pct[worst_idx]
        label.new(
            x=worst_idx, y=float(worst_val),
            text=f"Max DD\n{worst_val:.1f}%",
            style=label.style_label_up,
            color="rgba(183,28,28,0.4)",
            textcolor="#ef5350",
            size="small"
        )

# Current status label
if n > lookback and not np.isnan(drawdown_pct[-1]):
    curr_dd = float(drawdown_pct[-1])
    curr_dur = int(drawdown_duration[-1])
    curr_max = float(max_drawdown_rolling[-1]) if not np.isnan(max_drawdown_rolling[-1]) else 0.0
    label.new(
        x=n - 1, y=curr_dd,
        text=f"DD: {curr_dd:.1f}% | Dur: {curr_dur} | Max: {curr_max:.1f}%",
        style=label.style_label_left,
        color="rgba(239,83,80,0.3)",
        textcolor="#ef5350",
        size="normal"
    )
