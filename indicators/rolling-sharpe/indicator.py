from tg_scripting import *
import numpy as np

indicator("Rolling Risk-Adjusted Returns", overlay=False)

lookback = input.int(60, "Rolling Window", minval=20, maxval=252)
annual_factor = input.int(252, "Annualization Factor", minval=12, maxval=365)
risk_free = input.float(0.04, "Risk-Free Rate (Annual)", minval=0.0, maxval=0.15)
good_threshold = input.float(1.0, "Good Performance Threshold", minval=0.0, maxval=3.0)
poor_threshold = input.float(0.0, "Poor Performance Threshold", minval=-2.0, maxval=1.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")
label_cooldown = input.int(25, "Label Cooldown Bars", minval=5, maxval=50)

close_arr = np.array(close, dtype=np.float64)
n = len(close_arr)

# Daily returns
daily_returns = np.zeros(n)
for i in range(1, n):
    if close_arr[i - 1] > 0:
        daily_returns[i] = close_arr[i] / close_arr[i - 1] - 1.0

daily_rf = risk_free / annual_factor
excess_returns = daily_returns - daily_rf

# Rolling metrics
sharpe = np.full(n, np.nan)
sortino = np.full(n, np.nan)
calmar = np.full(n, np.nan)

for i in range(lookback, n):
    window = excess_returns[i - lookback + 1:i + 1]
    ret_window = daily_returns[i - lookback + 1:i + 1]

    mean_excess = np.mean(window)
    std_total = np.std(window)

    # Sharpe ratio (annualized)
    if std_total > 1e-10:
        sharpe[i] = (mean_excess / std_total) * np.sqrt(annual_factor)
    else:
        sharpe[i] = 0.0

    # Sortino ratio (downside deviation only)
    downside = window[window < 0]
    if len(downside) > 0:
        downside_std = np.sqrt(np.mean(downside ** 2))
        if downside_std > 1e-10:
            sortino[i] = (mean_excess / downside_std) * np.sqrt(annual_factor)
        else:
            sortino[i] = 0.0
    else:
        sortino[i] = float(sharpe[i]) * 1.5 if not np.isnan(sharpe[i]) else 0.0

    # Calmar ratio (return / max drawdown)
    price_window = close_arr[i - lookback + 1:i + 1]
    running_max = np.maximum.accumulate(price_window)
    drawdowns = (price_window / running_max - 1.0)
    max_dd = abs(np.min(drawdowns))

    total_return = (price_window[-1] / price_window[0] - 1.0)
    annualized_return = total_return * (annual_factor / lookback)

    if max_dd > 1e-10:
        calmar[i] = annualized_return / max_dd
    else:
        calmar[i] = annualized_return * 10.0  # Cap when no drawdown

# Clip extreme values for display
sharpe = np.clip(sharpe, -5.0, 5.0)
sortino = np.clip(sortino, -5.0, 8.0)
calmar = np.clip(calmar, -5.0, 10.0)

# Plots
plot(sharpe, title="Sharpe Ratio", color="#42A5F5")
plot(sortino, title="Sortino Ratio", color="#26A69A")
plot(calmar, title="Calmar Ratio", color="#FF9800")

if show_levels:
    hline(float(good_threshold), title="Good Performance", color="rgba(76,175,80,0.5)")
    hline(float(poor_threshold), title="Poor Performance", color="rgba(239,83,80,0.5)")
    hline(0.0, title="Zero Line", color="rgba(255,255,255,0.2)")

# Performance zones
good_zone = (sharpe > good_threshold) & (~np.isnan(sharpe))
poor_zone = (sharpe < poor_threshold) & (~np.isnan(sharpe))

bgcolor(good_zone, color="rgba(76,175,80,0.06)")
bgcolor(poor_zone, color="rgba(239,83,80,0.08)")

if show_labels:
    last_good = -label_cooldown
    last_poor = -label_cooldown

    for i in range(lookback, n):
        # Label transitions to good
        if good_zone[i] and not good_zone[i-1] and (i - last_good) > label_cooldown:
            label.new(
                x=i, y=float(sharpe[i]),
                text=f"Strong\nSR={sharpe[i]:.2f}",
                style=label.style_label_up,
                color="rgba(76,175,80,0.3)",
                textcolor="#4CAF50",
                size="small"
            )
            last_good = i

        if poor_zone[i] and not poor_zone[i-1] and (i - last_poor) > label_cooldown:
            label.new(
                x=i, y=float(sharpe[i]),
                text=f"Weak\nSR={sharpe[i]:.2f}",
                style=label.style_label_down,
                color="rgba(239,83,80,0.3)",
                textcolor="#ef5350",
                size="small"
            )
            last_poor = i

# Current status
if n > lookback and not np.isnan(sharpe[-1]):
    s = float(sharpe[-1])
    so = float(sortino[-1]) if not np.isnan(sortino[-1]) else 0.0
    c = float(calmar[-1]) if not np.isnan(calmar[-1]) else 0.0
    label.new(
        x=n - 1, y=s,
        text=f"SR: {s:.2f} | So: {so:.2f} | CR: {c:.2f}",
        style=label.style_label_left,
        color="rgba(66,165,245,0.3)",
        textcolor="#42A5F5",
        size="normal"
    )
