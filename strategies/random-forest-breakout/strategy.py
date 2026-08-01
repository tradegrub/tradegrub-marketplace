from tg_scripting import *
import numpy as np
from sklearn.ensemble import RandomForestClassifier

indicator("Random Forest Breakout", overlay=True)

length = input.int(20, "Lookback Length", minval=10, maxval=50)
n_trees = input.int(50, "Number of Trees", minval=10, maxval=200)
train_window = input.int(80, "Training Window", minval=40, maxval=150)
prob_thresh = input.float(0.65, "Probability Threshold", minval=0.5, maxval=0.9, step=0.05)
atr_mult = input.float(2.0, "ATR Stop Multiple", minval=1.0, maxval=5.0, step=0.5)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

atr_vals = np.array(ta.atr(high, low, close, length), dtype=float)
highest_vals = np.array(ta.highest(high, length), dtype=float)
lowest_vals = np.array(ta.lowest(low, length), dtype=float)

# Features
range_pos = np.where(highest_vals - lowest_vals > 0,
    (src - lowest_vals) / (highest_vals - lowest_vals), 0.5)
vol_ratio = np.zeros(n)
vol_sma = np.array(ta.sma(volume, length), dtype=float)
vol_ratio = np.where(vol_sma > 0, vol / vol_sma, 1.0)
atr_norm = np.zeros(n)
atr_sma = np.array(ta.sma(atr_vals.tolist(), length * 2), dtype=float)
atr_norm = np.where(atr_sma > 0, atr_vals / atr_sma, 1.0)

# Rolling return
ret_5 = np.zeros(n)
for i in range(5, n):
    ret_5[i] = (src[i] - src[i - 5]) / max(src[i - 5], 1e-10)

breakout_prob = np.full(n, 0.5)
start = train_window + length + 10

for i in range(start, n):
    ts = i - train_window
    X, y = [], []
    for j in range(ts, i - 5):
        X.append([range_pos[j], vol_ratio[j], atr_norm[j], ret_5[j]])
        future_ret = (src[min(j + 5, n - 1)] - src[j]) / max(src[j], 1e-10)
        y.append(1 if future_ret > atr_vals[j] * 0.5 / max(src[j], 1e-10) else 0)
    X = np.array(X)
    y = np.array(y)
    if len(np.unique(y)) < 2:
        continue
    rf = RandomForestClassifier(n_estimators=min(n_trees, 50), max_depth=4, random_state=42)
    rf.fit(X, y)
    xc = np.array([[range_pos[i], vol_ratio[i], atr_norm[i], ret_5[i]]])
    prob = rf.predict_proba(xc)
    if prob.shape[1] == 2:
        breakout_prob[i] = prob[0, 1]

# Signals
long_signal = np.zeros(n, dtype=bool)
for i in range(1, n):
    if breakout_prob[i] > prob_thresh and breakout_prob[i - 1] <= prob_thresh:
        long_signal[i] = True

in_position = False
for i in range(n):
    strategy.set_bar_index(i)
    if long_signal[i] and not in_position:
        strategy.entry("Long", strategy.LONG)
        sl = src[i] - atr_vals[i] * atr_mult
        tp = src[i] + atr_vals[i] * atr_mult * 1.5
        strategy.exit("Long", stop=sl, limit=tp)
        in_position = True
    elif in_position and breakout_prob[i] < 0.4:
        strategy.close("Long")
        in_position = False

plotshape(long_signal.tolist(), title="Breakout Signal", style="triangleup",
          location="belowbar", color="#00e676")
plot(breakout_prob.tolist(), title="Breakout Probability", color="#ff9800", linewidth=1)
hline(prob_thresh, title="Probability Threshold", color="#ffeb3b", linestyle="dashed")

bg_colors = [("rgba(76,175,80,0.12)" if breakout_prob[i] > prob_thresh else
              ("rgba(255,82,82,0.12)" if breakout_prob[i] < 0.4 else None)) for i in range(n)]
bgcolor(bg_colors, title="Probability Zone")
