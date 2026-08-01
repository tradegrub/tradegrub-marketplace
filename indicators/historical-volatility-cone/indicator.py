from tg_scripting import *
import numpy as np

indicator("Historical Volatility Cone", overlay=False)

base_len = input.int(20, "Base Length", minval=5, maxval=100)
annualize = input.int(252, "Annualization Factor", minval=1, maxval=365)
p25 = input.float(25.0, "Lower Percentile", minval=5.0, maxval=45.0, step=5.0)
p75 = input.float(75.0, "Upper Percentile", minval=55.0, maxval=95.0, step=5.0)

close_arr = np.array(close, dtype=float)
n = len(close_arr)

log_ret = np.zeros(n)
log_ret[1:] = np.log(close_arr[1:] / np.where(close_arr[:-1] > 0, close_arr[:-1], 1.0))

periods = [base_len, base_len * 2, base_len * 3]
hv_current = np.zeros(n)
hv_upper = np.zeros(n)
hv_lower = np.zeros(n)
hv_median = np.zeros(n)

for i in range(max(periods), n):
    vols = []
    for p in periods:
        window = log_ret[i - p + 1:i + 1]
        vol = np.std(window) * np.sqrt(annualize) * 100.0
        vols.append(vol)

    hv_current[i] = vols[0]
    all_vols = np.array(vols)
    hv_lower[i] = np.percentile(all_vols, p25)
    hv_upper[i] = np.percentile(all_vols, p75)
    hv_median[i] = np.median(all_vols)

plot(hv_current.tolist(), title="Current HV", color="#42A5F5", linewidth=2)
plot(hv_upper.tolist(), title="Upper Cone", color="#ff1744", linewidth=1)
plot(hv_lower.tolist(), title="Lower Cone", color="#00e676", linewidth=1)
plot(hv_median.tolist(), title="Median", color="#FFA726", linewidth=1)

high_vol = (hv_current > hv_upper).tolist()
low_vol = (hv_current < hv_lower).tolist()
bgcolor(high_vol, color="rgba(255,23,68,0.06)")
bgcolor(low_vol, color="rgba(0,230,118,0.06)")
