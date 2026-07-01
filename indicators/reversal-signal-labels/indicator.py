from tg_scripting import *
import numpy as np
from scipy.signal import argrelextrema

indicator("Reversal Signal Labels", overlay=True)

pivot_order = input.int(5, "Pivot Sensitivity", minval=2, maxval=15)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
vol_mult = input.float(1.5, "Volume Spike Mult", minval=1.0, maxval=3.0, step=0.25)
cooldown = input.int(10, "Label Cooldown", minval=5, maxval=30)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, rsi_len), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

vol_sma = np.array(ta.sma(volume, 20), dtype=float)
vol_sma = np.nan_to_num(vol_sma, nan=1.0)
vol_spike = vol > vol_sma * vol_mult

peaks = argrelextrema(hi, np.greater_equal, order=pivot_order)[0]
troughs = argrelextrema(lo, np.less_equal, order=pivot_order)[0]

bull_score = np.zeros(n)
bear_score = np.zeros(n)

for t in troughs:
    if t < n:
        score = 0
        if rsi_arr[t] < 35:
            score += 1
        if rsi_arr[t] < 25:
            score += 1
        if vol_spike[t]:
            score += 1
        bull_score[t] = score

for p in peaks:
    if p < n:
        score = 0
        if rsi_arr[p] > 65:
            score += 1
        if rsi_arr[p] > 75:
            score += 1
        if vol_spike[p]:
            score += 1
        bear_score[p] = score

last_bull = -cooldown
last_bear = -cooldown

for i in range(n):
    if bull_score[i] >= 2 and (i - last_bull) >= cooldown:
        last_bull = i
        strength = "STRONG" if bull_score[i] >= 3 else "MOD"
        color = "#00e676" if bull_score[i] >= 3 else "#66bb6a"
        label.new(x=i, y=float(lo[i]),
                  text=f"BUY {strength}",
                  style=label.style_label_up, color=color,
                  textcolor="#000000", size="small")

    if bear_score[i] >= 2 and (i - last_bear) >= cooldown:
        last_bear = i
        strength = "STRONG" if bear_score[i] >= 3 else "MOD"
        color = "#ff1744" if bear_score[i] >= 3 else "#ef5350"
        label.new(x=i, y=float(hi[i]),
                  text=f"SELL {strength}",
                  style=label.style_label_down, color=color,
                  textcolor="#ffffff", size="small")
