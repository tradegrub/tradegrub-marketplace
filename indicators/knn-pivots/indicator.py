from tg_scripting import *
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

indicator("KNN Pivot Prediction", overlay=False)

k_neighbors = input.int(5, "K Neighbors", minval=3, maxval=20)
feature_len = input.int(10, "Feature Lookback", minval=3, maxval=50)
train_len = input.int(100, "Training Window", minval=50, maxval=500)
prob_smooth = input.int(3, "Probability Smoothing", minval=1, maxval=10)
conf_band = input.float(0.3, "Confidence Band Width", minval=0.05, maxval=0.5, step=0.05)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

close_arr = np.array(close, dtype=np.float64)
high_arr = np.array(high, dtype=np.float64)
low_arr = np.array(low, dtype=np.float64)
vol_arr = np.array(volume, dtype=np.float64)
n = len(close_arr)

# Feature engineering
returns = np.zeros(n)
volatility = np.zeros(n)
vol_ratio = np.zeros(n)
momentum = np.zeros(n)

vol_ma = np.array(ta.sma(volume, feature_len), dtype=np.float64)

for i in range(feature_len, n):
    returns[i] = (close_arr[i] / close_arr[i - feature_len] - 1.0) * 100.0
    volatility[i] = np.std(close_arr[i - feature_len:i]) / close_arr[i] * 100.0
    if vol_ma[i] > 0:
        vol_ratio[i] = vol_arr[i] / vol_ma[i]
    hl_range = high_arr[i - feature_len:i].max() - low_arr[i - feature_len:i].min()
    if hl_range > 0:
        momentum[i] = (close_arr[i] - low_arr[i - feature_len:i].min()) / hl_range * 100.0

# Labels: 1 if next bar closes higher, 0 otherwise
labels = np.zeros(n, dtype=np.int32)
for i in range(n - 1):
    labels[i] = 1 if close_arr[i + 1] > close_arr[i] else 0

# Rolling KNN prediction
prob_up = np.full(n, 0.5)
prediction = np.zeros(n, dtype=np.int32)
confidence = np.zeros(n)

start_idx = feature_len + train_len
if start_idx < n:
    features_all = np.column_stack([returns, volatility, vol_ratio, momentum])

    for i in range(start_idx, n):
        train_start = max(feature_len, i - train_len)
        train_end = i - 1

        X_train = features_all[train_start:train_end]
        y_train = labels[train_start:train_end]

        if len(np.unique(y_train)) < 2:
            continue

        valid = np.all(np.isfinite(X_train), axis=1)
        X_train = X_train[valid]
        y_train = y_train[valid]

        if len(X_train) < k_neighbors * 2:
            continue

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)

        knn = KNeighborsClassifier(n_neighbors=min(k_neighbors, len(X_train)))
        knn.fit(X_scaled, y_train)

        x_current = features_all[i:i + 1]
        if np.all(np.isfinite(x_current)):
            x_scaled = scaler.transform(x_current)
            proba = knn.predict_proba(x_scaled)
            class_list = list(knn.classes_)
            if 1 in class_list:
                prob_up[i] = proba[0][class_list.index(1)]
            prediction[i] = knn.predict(x_scaled)[0]
            confidence[i] = abs(prob_up[i] - 0.5) * 2

prob_smooth_arr = np.array(ta.sma(prob_up, prob_smooth), dtype=np.float64)

# Plotting
plot(prob_smooth_arr * 100, title="Bullish Probability %", color="#42A5F5")
plot(confidence * 100, title="Confidence %", color="#FF9800")

h_upper = hline(50 + conf_band * 100, title="Upper Confidence", color="rgba(102,187,106,0.5)")
h_lower = hline(50 - conf_band * 100, title="Lower Confidence", color="rgba(239,83,80,0.5)")
hline(50, title="Neutral", color="rgba(128,128,128,0.3)")

bgcolor(prob_smooth_arr > 0.5 + conf_band, color="rgba(102,187,106,0.06)")
bgcolor(prob_smooth_arr < 0.5 - conf_band, color="rgba(239,83,80,0.06)")

if show_labels:
    last_bull_idx = -30
    last_bear_idx = -30
    cooldown = 20
    for i in range(1, n):
        if prob_smooth_arr[i] > 0.5 + conf_band and prob_smooth_arr[i - 1] <= 0.5 + conf_band and (i - last_bull_idx) > cooldown:
            last_bull_idx = i
            label.new(x=i, y=float(prob_smooth_arr[i] * 100),
                      text="Bullish\nPivot",
                      style=label.style_label_down, color="rgba(102,187,106,0.2)",
                      textcolor="#66bb6a", size="small")
        if prob_smooth_arr[i] < 0.5 - conf_band and prob_smooth_arr[i - 1] >= 0.5 - conf_band and (i - last_bear_idx) > cooldown:
            last_bear_idx = i
            label.new(x=i, y=float(prob_smooth_arr[i] * 100),
                      text="Bearish\nPivot",
                      style=label.style_label_up, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")

if show_levels:
    accuracy = 0
    total = 0
    for i in range(start_idx, n - 1):
        if confidence[i] > 0.3:
            total += 1
            if prediction[i] == labels[i]:
                accuracy += 1
    acc_pct = (accuracy / total * 100) if total > 0 else 0
    label.new(x=n - 1, y=float(50 + conf_band * 100 + 8),
              text=f"Accuracy: {acc_pct:.1f}%\nSamples: {total}",
              style=label.style_label_left, color="rgba(66,165,245,0.15)",
              textcolor="#90caf9", size="small")
