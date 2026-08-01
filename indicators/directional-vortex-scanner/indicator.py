from tg_scripting import *
import numpy as np

indicator("Directional Vortex Scanner", overlay=False)

length = input.int(14, "Vortex Length", minval=5, maxval=50)
confirm_len = input.int(21, "Confirmation Length", minval=10, maxval=60)
threshold = input.float(0.1, "Signal Threshold", minval=0.02, maxval=0.5, step=0.02)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

vm_plus = np.zeros(n)
vm_minus = np.zeros(n)
tr_sum = np.zeros(n)
for i in range(1, n):
    vm_plus[i] = abs(hi[i] - lo[i-1])
    vm_minus[i] = abs(lo[i] - hi[i-1])
    tr_sum[i] = max(hi[i] - lo[i], abs(hi[i] - cl[i-1]), abs(lo[i] - cl[i-1]))

vi_plus = np.zeros(n)
vi_minus = np.zeros(n)
for i in range(length, n):
    tr_total = np.sum(tr_sum[i-length+1:i+1])
    if tr_total > 0:
        vi_plus[i] = np.sum(vm_plus[i-length+1:i+1]) / tr_total
        vi_minus[i] = np.sum(vm_minus[i-length+1:i+1]) / tr_total

vi_diff = vi_plus - vi_minus

vi_plus_long = np.zeros(n)
vi_minus_long = np.zeros(n)
for i in range(confirm_len, n):
    tr_total = np.sum(tr_sum[i-confirm_len+1:i+1])
    if tr_total > 0:
        vi_plus_long[i] = np.sum(vm_plus[i-confirm_len+1:i+1]) / tr_total
        vi_minus_long[i] = np.sum(vm_minus[i-confirm_len+1:i+1]) / tr_total

confirmed_bull = (vi_diff > threshold) & (vi_plus_long > vi_minus_long)
confirmed_bear = (vi_diff < -threshold) & (vi_plus_long < vi_minus_long)

plot(vi_plus.tolist(), title="VI+", color="#4CAF50", linewidth=2)
plot(vi_minus.tolist(), title="VI-", color="#f44336", linewidth=2)
plot(vi_diff.tolist(), title="Vortex Diff", color="#42a5f5", linewidth=1)
hline(1.0, title="Baseline", color="#888888", linestyle="dashed")
bgcolor(confirmed_bull.tolist(), color="rgba(76,175,80,0.08)")
bgcolor(confirmed_bear.tolist(), color="rgba(244,67,54,0.08)")
