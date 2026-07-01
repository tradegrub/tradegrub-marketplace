from tg_scripting import *
import numpy as np

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

indicator("Gradient Boosted Signals", overlay=False)

length = input.int(14, "Feature Length", minval=5, maxval=50)
train_window = input.int(80, "Training Window", minval=40, maxval=150)
threshold = input.float(0.6, "Signal Threshold", minval=0.5, maxval=0.9, step=0.05)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

rsi_vals = np.array(ta.rsi(close, length), dtype=float)
macd_line, macd_sig, macd_hist = ta.macd(close, 12, 26, 9)
macd_h = np.array(macd_hist, dtype=float)
atr_vals = np.array(ta.atr(high, low, close, length), dtype=float)
bb_upper, bb_mid, bb_lower = ta.bb(close, 20, 2.0)
bb_u = np.array(bb_upper, dtype=float)
bb_l = np.array(bb_lower, dtype=float)
bb_pos = np.where(bb_u - bb_l > 0, (src - bb_l) / (bb_u - bb_l), 0.5)

vol_sma = np.array(ta.sma(volume, length), dtype=float)
vol_ratio = np.where(vol_sma > 0, vol / vol_sma, 1.0)

signal_score = np.full(n, 50.0)
start = train_window + 30

for i in range(start, n):
    ts = i - train_window
    X, y = [], []
    for j in range(ts, i - 3):
        X.append([rsi_vals[j], macd_h[j], bb_pos[j], vol_ratio[j],
                  atr_vals[j] / max(src[j], 1e-10)])
        future = (src[min(j + 3, n - 1)] - src[j]) / max(src[j], 1e-10)
        y.append(1 if future > 0 else 0)
    X = np.array(X)
    y = np.array(y)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    if len(np.unique(y)) < 2:
        continue

    if HAS_LGB:
        ds = lgb.Dataset(X, label=y)
        params = {"objective": "binary", "num_leaves": 8, "learning_rate": 0.1,
                  "verbose": -1, "n_estimators": 30}
        model = lgb.train(params, ds, num_boost_round=30)
        xc = np.array([[rsi_vals[i], macd_h[i], bb_pos[i], vol_ratio[i],
                        atr_vals[i] / max(src[i], 1e-10)]])
        prob = model.predict(xc)[0]
    else:
        # Numpy fallback: simple logistic-style scoring
        mu = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        std[std == 0] = 1
        Xn = (X - mu) / std
        y_f = y.astype(float)
        try:
            weights = np.linalg.lstsq(Xn, y_f, rcond=None)[0]
        except np.linalg.LinAlgError:
            weights = np.dot(np.linalg.pinv(Xn), y_f)
        xc = np.array([rsi_vals[i], macd_h[i], bb_pos[i], vol_ratio[i],
                       atr_vals[i] / max(src[i], 1e-10)])
        xc_n = (xc - mu) / std
        raw = np.dot(xc_n, weights)
        prob = 1 / (1 + np.exp(-raw))

    signal_score[i] = prob * 100

smoothed = np.array(ta.sma(signal_score.tolist(), 3), dtype=float)

plot(smoothed.tolist(), title="Signal Score", color="#ff6f00", linewidth=2)
hline(threshold * 100, title="Bullish Threshold", color="#4CAF50", linestyle="dashed")
hline((1 - threshold) * 100, title="Bearish Threshold", color="#f44336", linestyle="dashed")
hline(50, title="Neutral", color="#888888", linestyle="dashed")
