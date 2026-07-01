from tg_scripting import *
import numpy as np

indicator("Correlation Risk Manager", overlay=False)

length = input.int(30, "Lookback Length", minval=10, maxval=100)
warn_thresh = input.float(0.7, "Warning Threshold", minval=0.3, maxval=0.95, step=0.05)
danger_thresh = input.float(0.85, "Danger Threshold", minval=0.5, maxval=0.99, step=0.05)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

# Compute returns
ret = np.diff(src, prepend=src[0]) / np.where(src == 0, 1, src)

# Compute rolling correlation between price returns and volume changes
vol_ret = np.diff(vol, prepend=vol[0]) / np.where(vol == 0, 1, vol)

corr_pv = np.zeros(n)
for i in range(length, n):
    window_r = ret[i - length:i]
    window_v = vol_ret[i - length:i]
    std_r = np.std(window_r)
    std_v = np.std(window_v)
    if std_r > 0 and std_v > 0:
        corr_pv[i] = np.corrcoef(window_r, window_v)[0, 1]

# Compute rolling autocorrelation of returns (concentration risk proxy)
autocorr = np.zeros(n)
for i in range(length + 1, n):
    w1 = ret[i - length:i]
    w2 = ret[i - length - 1:i - 1]
    s1, s2 = np.std(w1), np.std(w2)
    if s1 > 0 and s2 > 0:
        autocorr[i] = np.corrcoef(w1, w2)[0, 1]

# Composite risk score: blend absolute correlation and autocorrelation
abs_corr = np.abs(corr_pv)
abs_auto = np.abs(autocorr)
risk_score = 0.6 * abs_corr + 0.4 * abs_auto
risk_score = np.clip(risk_score, 0, 1)

# Smooth the risk score
smooth_risk = ta.sma(risk_score.tolist(), 5)
smooth_risk = np.array(smooth_risk, dtype=float)

# Conditions
warn_zone = smooth_risk > warn_thresh
danger_zone = smooth_risk > danger_thresh
safe_zone = smooth_risk <= warn_thresh

plot(smooth_risk.tolist(), title="Risk Score", color="#ff9800", linewidth=2)
plot(corr_pv.tolist(), title="Price-Volume Corr", color="#42a5f5", linewidth=1)

hline(warn_thresh, title="Warning", color="#ffeb3b", linestyle="dashed")
hline(danger_thresh, title="Danger", color="#f44336", linestyle="dashed")

bgcolor(danger_zone.tolist(), color="rgba(244,67,54,0.12)")
bgcolor(warn_zone.tolist(), color="rgba(255,152,0,0.08)")
bgcolor(safe_zone.tolist(), color="rgba(76,175,80,0.04)")
