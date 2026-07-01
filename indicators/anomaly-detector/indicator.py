from tg_scripting import *
import numpy as np
from sklearn.ensemble import IsolationForest

indicator("Anomaly Detector", overlay=False)

length = input.int(14, "Feature Length", minval=5, maxval=50)
train_window = input.int(100, "Training Window", minval=50, maxval=200)
contamination = input.float(0.05, "Contamination", minval=0.01, maxval=0.2, step=0.01)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

# Features
ret = np.zeros(n)
for i in range(1, n):
    ret[i] = (src[i] - src[i - 1]) / max(src[i - 1], 1e-10) * 100

atr_vals = np.array(ta.atr(high, low, close, length), dtype=float)
vol_sma = np.array(ta.sma(volume, length), dtype=float)
vol_ratio = np.where(vol_sma > 0, vol / vol_sma, 1.0)

body_ratio = np.abs(src - np.array(open, dtype=float)) / np.where(hi - lo > 0, hi - lo, 1)
range_norm = (hi - lo) / np.where(atr_vals > 0, atr_vals, 1)

anomaly_score = np.zeros(n)
is_anomaly = np.zeros(n, dtype=bool)
start = train_window + length + 5

for i in range(start, n):
    ts = i - train_window
    X = []
    for j in range(ts, i + 1):
        X.append([ret[j], vol_ratio[j], body_ratio[j], range_norm[j]])
    X = np.array(X)

    iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=50)
    iso.fit(X[:-1])

    score = iso.decision_function(X[-1:])
    pred = iso.predict(X[-1:])
    anomaly_score[i] = -score[0]  # Higher = more anomalous
    is_anomaly[i] = pred[0] == -1

# Normalize anomaly score to 0-100
valid = anomaly_score[start:]
if len(valid) > 0:
    mn, mx = np.min(valid), np.max(valid)
    if mx > mn:
        anomaly_score[start:] = (anomaly_score[start:] - mn) / (mx - mn) * 100

alert_level = anomaly_score > 70

plot(anomaly_score.tolist(), title="Anomaly Score", color="#ff5252", linewidth=2)
hline(70, title="Alert Level", color="#ff9800", linestyle="dashed")
hline(30, title="Normal", color="#4CAF50", linestyle="dashed")
bgcolor(alert_level.tolist(), color="rgba(255,82,82,0.10)")
plotshape(is_anomaly.tolist(), title="Anomaly Detected", style="triangledown",
          location="belowbar", color="#ff5252")
