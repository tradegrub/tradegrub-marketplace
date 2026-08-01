from tg_scripting import *
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

indicator("ML Momentum Index", overlay=False)

mom_len = input.int(14, "Momentum Length", minval=5, maxval=50)
k_neighbors = input.int(5, "K Neighbors", minval=3, maxval=21)
lookback = input.int(60, "Training Lookback", minval=30, maxval=150)

src = np.array(close, dtype=float)
n = len(src)

# Traditional momentum
mom = np.zeros(n)
for i in range(mom_len, n):
    mom[i] = (src[i] - src[i - mom_len]) / src[i - mom_len] * 100

rsi_vals = np.array(ta.rsi(close, mom_len), dtype=float)
roc = np.zeros(n)
for i in range(1, n):
    roc[i] = (src[i] - src[i - 1]) / max(src[i - 1], 1e-10) * 100

# Build features and labels for KNN
ml_score = np.full(n, 50.0)
start = max(lookback + 10, mom_len + 10)

for i in range(start, n):
    train_end = i
    train_start = i - lookback
    X_train = []
    y_train = []
    for j in range(train_start, train_end - 1):
        X_train.append([mom[j], rsi_vals[j], roc[j]])
        y_train.append(1 if src[j + 1] > src[j] else 0)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    valid = ~np.any(np.isnan(X_train), axis=1)
    X_train = X_train[valid]
    y_train = y_train[valid]

    if len(X_train) < k_neighbors + 2 or len(np.unique(y_train)) < 2:
        continue

    if np.isnan(mom[i]) or np.isnan(rsi_vals[i]) or np.isnan(roc[i]):
        continue

    std = np.std(X_train, axis=0)
    std[std == 0] = 1
    mean = np.mean(X_train, axis=0)
    X_norm = (X_train - mean) / std

    knn = KNeighborsClassifier(n_neighbors=min(k_neighbors, len(X_train)))
    knn.fit(X_norm, y_train)

    x_cur = np.array([[mom[i], rsi_vals[i], roc[i]]])
    x_cur_norm = (x_cur - mean) / std
    prob = knn.predict_proba(x_cur_norm)
    if prob.shape[1] == 2:
        ml_score[i] = prob[0, 1] * 100

# Blend traditional momentum (normalized) with ML score
mom_norm = np.zeros(n)
for i in range(start, n):
    window = mom[max(0, i - lookback):i + 1]
    mn, mx = np.min(window), np.max(window)
    if mx > mn:
        mom_norm[i] = (mom[i] - mn) / (mx - mn) * 100

blended = 0.5 * mom_norm + 0.5 * ml_score


plot(blended.tolist(), title="ML Momentum Index", color="#e040fb", linewidth=2)
plot(ml_score.tolist(), title="ML Score", color="#42a5f5", linewidth=1)
hline(60, title="Bullish", color="#4CAF50", linestyle="dashed")
hline(40, title="Bearish", color="#f44336", linestyle="dashed")
hline(50, title="Neutral", color="#888888", linestyle="dashed")
