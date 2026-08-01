from tg_scripting import *
import numpy as np

indicator("Consolidation Scanner", overlay=False)

length = input.int(20, "Lookback Length", minval=10, maxval=60)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
threshold = input.float(0.3, "Consolidation Threshold", minval=0.1, maxval=0.8, step=0.05)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

range_ratio = np.zeros(n)
atr_percentile = np.zeros(n)
consol_score = np.zeros(n)

for i in range(length, n):
    period_range = np.max(hi[i-length:i+1]) - np.min(lo[i-length:i+1])
    avg_atr = np.mean(atr_arr[i-length:i+1])
    expected_range = avg_atr * length * 0.3
    range_ratio[i] = period_range / max(expected_range, 1e-10)

    atr_window = atr_arr[max(0,i-100):i+1]
    atr_percentile[i] = np.sum(atr_window <= atr_arr[i]) / max(len(atr_window), 1) * 100

    consol_score[i] = (1 - min(range_ratio[i], 2) / 2) * 50 + (100 - atr_percentile[i]) / 2

is_consolidating = consol_score > (1 - threshold) * 100

plot(consol_score.tolist(), title="Consolidation Score", color="#ab47bc", linewidth=2)
plot(atr_percentile.tolist(), title="ATR Percentile", color="#78909C", linewidth=1)
hline((1-threshold)*100, title="Consolidation Zone", color="#ff9800", linestyle="dashed")
hline(50, title="Mid", color="#888888", linestyle="dashed")
bgcolor(is_consolidating.tolist(), color="rgba(171,71,188,0.08)")
