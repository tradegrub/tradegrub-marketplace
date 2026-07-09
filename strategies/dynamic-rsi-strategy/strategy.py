from tg_scripting import *
import numpy as np

indicator("Dynamic RSI Strategy", overlay=True)

base_len = input.int(14, "Base RSI Length", minval=5, maxval=30)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
stop_mult = input.float(2.0, "Stop ATR Mult", minval=1.0, maxval=4.0, step=0.5)
tp_mult = input.float(2.5, "TP ATR Mult", minval=1.0, maxval=5.0, step=0.5)

cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

atr_pct = np.zeros(n)
for i in range(50, n):
    window = atr_arr[i-50:i]
    atr_pct[i] = np.sum(window <= atr_arr[i]) / 50

adaptive_len = np.zeros(n, dtype=int)
for i in range(n):
    vol_adj = 0.5 + atr_pct[i]
    adaptive_len[i] = max(5, min(30, int(base_len * vol_adj)))

rsi_arr = np.array(ta.rsi(close, base_len), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

ob_level = np.zeros(n)
os_level = np.zeros(n)
for i in range(n):
    spread = 20 + 10 * atr_pct[i]
    ob_level[i] = 50 + spread
    os_level[i] = 50 - spread

long_sig = np.zeros(n, dtype=bool)
short_sig = np.zeros(n, dtype=bool)
for i in range(1, n):
    if rsi_arr[i] > os_level[i] and rsi_arr[i-1] <= os_level[i-1]:
        long_sig[i] = True
    if rsi_arr[i] < ob_level[i] and rsi_arr[i-1] >= ob_level[i-1]:
        short_sig[i] = True

in_long = False
in_short = False
entry_price = 0.0
for i in range(base_len, n):
    strategy.set_bar_index(i)
    if long_sig[i] and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price = float(cl[i])
    elif short_sig[i] and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price = float(cl[i])

    if in_long:
        sl = entry_price - atr_arr[i] * stop_mult
        tp = entry_price + atr_arr[i] * tp_mult
        strategy.exit("Long", stop=sl, limit=tp)
        if cl[i] <= sl or cl[i] >= tp:
            in_long = False
    if in_short:
        sl = entry_price + atr_arr[i] * stop_mult
        tp = entry_price - atr_arr[i] * tp_mult
        strategy.exit("Short", stop=sl, limit=tp)
        if cl[i] >= sl or cl[i] <= tp:
            in_short = False

plotshape(long_sig.tolist(), title="Long", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(short_sig.tolist(), title="Short", style="triangledown", location="abovebar", color="#ff1744", size="small")

# RSI line and its dynamic overbought/oversold bands (matches concept sub-panel)
plot(rsi_arr.tolist(), title="RSI", color="#ab47bc", width=2)
ob_plot = plot(ob_level.tolist(), title="Overbought Band", color="#ff9800", style="dashed")
os_plot = plot(os_level.tolist(), title="Oversold Band", color="#42a5f5", style="dashed")
fill(ob_plot, os_plot, color="rgba(171,71,188,0.04)")

# Highlight bars where a buy/exit signal fires
bgcolor([("rgba(0,230,118,0.12)" if long_sig[i] else ("rgba(239,83,80,0.12)" if short_sig[i] else None)) for i in range(n)])
