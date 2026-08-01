from tg_scripting import *
import numpy as np

indicator("Multi Period Opens", overlay=True)

show_daily = input.bool(True, "Show Daily Open")
show_weekly = input.bool(True, "Show Weekly Open")
show_monthly = input.bool(True, "Show Monthly Open")
show_yearly = input.bool(True, "Show Yearly Open")

cl = np.array(close, dtype=float)
n = len(cl)

DAILY_BARS = 1
WEEKLY_BARS = 5
MONTHLY_BARS = 21
YEARLY_BARS = 252

def period_open(lookback):
    result = np.full(n, np.nan)
    for i in range(lookback, n):
        result[i] = cl[i - lookback]
    return result

if show_daily and n > DAILY_BARS:
    d_open = period_open(DAILY_BARS)
    plot(d_open[DAILY_BARS:].tolist(), title="Daily Open", color="#42a5f5", linewidth=1)

if show_weekly and n > WEEKLY_BARS:
    w_open = period_open(WEEKLY_BARS)
    plot(w_open[WEEKLY_BARS:].tolist(), title="Weekly Open", color="#ab47bc", linewidth=1)

if show_monthly and n > MONTHLY_BARS:
    m_open = period_open(MONTHLY_BARS)
    plot(m_open[MONTHLY_BARS:].tolist(), title="Monthly Open", color="#FF9800", linewidth=1)

if show_yearly and n > YEARLY_BARS:
    y_open = period_open(YEARLY_BARS)
    plot(y_open[YEARLY_BARS:].tolist(), title="Yearly Open", color="#4CAF50", linewidth=1)

if n > YEARLY_BARS + 5:
    if show_daily:
        label.new(x=n-1, y=float(d_open[n-1]),
                  text=f"D Open: {d_open[n-1]:.2f}",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor="#42a5f5", size="small")
    if show_weekly:
        label.new(x=n-1, y=float(w_open[n-1]),
                  text=f"W Open: {w_open[n-1]:.2f}",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor="#ab47bc", size="small")
    if show_monthly:
        label.new(x=n-1, y=float(m_open[n-1]),
                  text=f"M Open: {m_open[n-1]:.2f}",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor="#FF9800", size="small")
    if show_yearly:
        label.new(x=n-1, y=float(y_open[n-1]),
                  text=f"Y Open: {y_open[n-1]:.2f}",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor="#4CAF50", size="small")
