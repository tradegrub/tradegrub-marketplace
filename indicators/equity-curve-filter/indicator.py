from tg_scripting import *
import numpy as np

indicator("Equity Curve Trading Filter", overlay=False)

ma_len = input.int(20, "Equity MA Length", minval=5, maxval=100)
signal_len = input.int(14, "Signal Length", minval=5, maxval=50)
pause_dd = input.float(5.0, "Pause Drawdown %", minval=1.0, maxval=20.0, step=0.5)

n = len(close)
equity = np.zeros(n)
equity[0] = 100.0

sma_fast = ta.sma(close, signal_len)
sma_slow = ta.sma(close, signal_len * 2)

position = 0
for i in range(1, n):
    pnl = 0.0
    if position == 1:
        pnl = (close[i] - close[i - 1]) / close[i - 1] * equity[i - 1]
    elif position == -1:
        pnl = (close[i - 1] - close[i]) / close[i - 1] * equity[i - 1]
    equity[i] = equity[i - 1] + pnl

    if not np.isnan(sma_fast[i]) and not np.isnan(sma_slow[i]):
        if sma_fast[i] > sma_slow[i]:
            position = 1
        else:
            position = -1
    else:
        position = 0

equity_ma = ta.sma(equity, ma_len)
eq_peak = np.zeros(n)
eq_peak[0] = equity[0]
for i in range(1, n):
    eq_peak[i] = max(eq_peak[i - 1], equity[i])

drawdown = np.zeros(n)
for i in range(n):
    drawdown[i] = (equity[i] - eq_peak[i]) / eq_peak[i] * 100.0 if eq_peak[i] > 0 else 0

trading_on = np.zeros(n, dtype=bool)
trading_off = np.zeros(n, dtype=bool)
for i in range(n):
    ema_ok = not np.isnan(equity_ma[i]) and equity[i] >= equity_ma[i]
    dd_ok = drawdown[i] > -pause_dd
    trading_on[i] = ema_ok and dd_ok
    trading_off[i] = not trading_on[i]

filtered_equity = np.zeros(n)
filtered_equity[0] = 100.0
for i in range(1, n):
    if trading_on[i]:
        change = (equity[i] - equity[i - 1])
        filtered_equity[i] = filtered_equity[i - 1] + change
    else:
        filtered_equity[i] = filtered_equity[i - 1]

plot(equity, title="Raw Equity", color="#42a5f5", linewidth=1)
plot(equity_ma, title="Equity MA", color="#ffa726", linewidth=1)
plot(filtered_equity, title="Filtered Equity", color="#00e676", linewidth=2)
bgcolor(trading_off, color="rgba(255,82,82,0.06)")
bgcolor(trading_on, color="rgba(76,175,80,0.04)")
