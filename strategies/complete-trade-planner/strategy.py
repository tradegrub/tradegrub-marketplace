from tg_scripting import *
import numpy as np

indicator("Complete Trade Planner", overlay=True)

rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
ma_len = input.int(20, "MA Length", minval=10, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
sl_mult = input.float(2.0, "Stop Loss ATR Mult", minval=1.0, maxval=5.0, step=0.5)
tp_mult = input.float(3.0, "Take Profit ATR Mult", minval=1.5, maxval=6.0, step=0.5)
trail_mult = input.float(1.5, "Trailing Stop ATR Mult", minval=0.5, maxval=3.0, step=0.5)
min_signals = input.int(2, "Min Signals for Entry", minval=1, maxval=3)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, rsi_len), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

sma_arr = np.array(ta.sma(close, ma_len), dtype=float)
sma_arr = np.nan_to_num(sma_arr, nan=0.0)

macd_l, macd_s, macd_h = ta.macd(close, 12, 26, 9)
macd_hist = np.array(macd_h, dtype=float)
macd_hist = np.nan_to_num(macd_hist, nan=0.0)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

long_score = np.zeros(n, dtype=int)
short_score = np.zeros(n, dtype=int)
for i in range(ma_len, n):
    if rsi_arr[i] < 40:
        long_score[i] += 1
    if rsi_arr[i] > 60:
        short_score[i] += 1
    if cl[i] > sma_arr[i]:
        long_score[i] += 1
    if cl[i] < sma_arr[i]:
        short_score[i] += 1
    if macd_hist[i] > 0:
        long_score[i] += 1
    if macd_hist[i] < 0:
        short_score[i] += 1

in_long = False
in_short = False
entry_price = 0.0
trail_stop = 0.0

for i in range(ma_len, n):
    if long_score[i] >= min_signals and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price = float(cl[i])
        trail_stop = entry_price - atr_arr[i] * trail_mult
    elif short_score[i] >= min_signals and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price = float(cl[i])
        trail_stop = entry_price + atr_arr[i] * trail_mult

    if in_long:
        sl = entry_price - atr_arr[i] * sl_mult
        tp = entry_price + atr_arr[i] * tp_mult
        trail_stop = max(trail_stop, float(cl[i]) - atr_arr[i] * trail_mult)
        effective_stop = max(sl, trail_stop)
        strategy.exit("Long", stop=effective_stop, limit=tp)
        if cl[i] <= effective_stop or cl[i] >= tp:
            in_long = False

    if in_short:
        sl = entry_price + atr_arr[i] * sl_mult
        tp = entry_price - atr_arr[i] * tp_mult
        trail_stop = min(trail_stop, float(cl[i]) + atr_arr[i] * trail_mult)
        effective_stop = min(sl, trail_stop)
        strategy.exit("Short", stop=effective_stop, limit=tp)
        if cl[i] >= effective_stop or cl[i] <= tp:
            in_short = False

long_entry = long_score >= min_signals
short_entry = short_score >= min_signals
plotshape(long_entry.tolist(), title="Long Signal", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(short_entry.tolist(), title="Short Signal", style="triangledown", location="abovebar", color="#ff1744", size="small")
plot(sma_arr.tolist(), title="Trend MA", color="#42a5f5", linewidth=1)
