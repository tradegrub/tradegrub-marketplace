from tg_scripting import *
import numpy as np

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

indicator("Regime Classifier", overlay=False)

length = input.int(14, "Feature Length", minval=5, maxval=50)
train_window = input.int(80, "Training Window", minval=40, maxval=150)
smooth = input.int(3, "Smoothing", minval=1, maxval=10)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

rsi_vals = np.array(ta.rsi(close, length), dtype=float)
atr_vals = np.array(ta.atr(high, low, close, length), dtype=float)
sma_short = np.array(ta.sma(close, length), dtype=float)
sma_long = np.array(ta.sma(close, length * 2), dtype=float)

# Features
trend_strength = (sma_short - sma_long) / np.where(atr_vals == 0, 1, atr_vals)
volatility = atr_vals / np.where(src == 0, 1, src) * 100
rsi_norm = rsi_vals / 100.0

# Labels: 0=range, 1=bull, 2=bear
def make_label(ret, vol_pct):
    if abs(ret) < vol_pct * 0.3:
        return 0  # range
    return 1 if ret > 0 else 2

regime_raw = np.zeros(n)
start = train_window + length * 2 + 10

for i in range(start, n):
    ts = i - train_window
    X, y = [], []
    for j in range(ts, i - 5):
        X.append([trend_strength[j], volatility[j], rsi_norm[j]])
        ret_5 = (src[min(j + 5, n - 1)] - src[j]) / max(src[j], 1e-10)
        y.append(make_label(ret_5, volatility[j]))
    X = np.array(X)
    y = np.array(y)
    if len(np.unique(y)) < 2:
        continue

    if HAS_XGB:
        dtrain = xgb.DMatrix(X, label=y)
        params = {"max_depth": 3, "eta": 0.1, "objective": "multi:softprob",
                  "num_class": 3, "verbosity": 0}
        model = xgb.train(params, dtrain, num_boost_round=20)
        xc = xgb.DMatrix(np.array([[trend_strength[i], volatility[i], rsi_norm[i]]]))
        probs = model.predict(xc)[0]
    else:
        # Numpy fallback
        mu = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        std[std == 0] = 1
        xc = np.array([trend_strength[i], volatility[i], rsi_norm[i]])
        xc_n = (xc - mu) / std
        # Simple heuristic
        if xc_n[0] > 0.5 and xc_n[2] > 0:
            probs = [0.1, 0.7, 0.2]
        elif xc_n[0] < -0.5 and xc_n[2] < 0:
            probs = [0.1, 0.2, 0.7]
        else:
            probs = [0.6, 0.2, 0.2]

    # Score: bull prob - bear prob, range from -1 to 1
    regime_raw[i] = probs[1] - probs[2]

smoothed = np.array(ta.sma(regime_raw.tolist(), smooth), dtype=float)
regime_score = smoothed * 100

bull_regime = regime_score > 25
bear_regime = regime_score < -25
range_regime = (~bull_regime) & (~bear_regime)

plot(regime_score.tolist(), title="Regime Score", color="#ab47bc", linewidth=2)
hline(25, title="Bull Zone", color="#4CAF50", linestyle="dashed")
hline(-25, title="Bear Zone", color="#f44336", linestyle="dashed")
hline(0, title="Neutral", color="#888888", linestyle="dashed")
bgcolor(bull_regime.tolist(), color="rgba(76,175,80,0.06)")
bgcolor(bear_regime.tolist(), color="rgba(244,67,54,0.06)")
bgcolor(range_regime.tolist(), color="rgba(255,193,7,0.04)")
