from tg_scripting import *
import numpy as np

lookback = input.int(200, "Training Lookback", minval=50, maxval=500)
threshold = input.float(0.6, "Signal Threshold", minval=0.5, maxval=0.9)
rsi_period = input.int(14, "RSI Period", minval=5, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=5, maxval=30)
macd_slow = input.int(26, "MACD Slow", minval=15, maxval=50)

rsi = ta.rsi(close, rsi_period)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, 9)
vol_sma = ta.sma(volume, 20)
vol_ratio = volume / vol_sma

features = np.column_stack([
    rsi[-lookback:],
    macd_line[-lookback:],
    hist[-lookback:],
    vol_ratio[-lookback:],
    ta.roc(close, 5)[-lookback:],
    ta.roc(close, 10)[-lookback:],
])

future_returns = np.sign(np.diff(close[-lookback - 1:]))

from sklearn.ensemble import GradientBoostingClassifier
model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
train_X = features[:-1]
train_y = (future_returns > 0).astype(int)
model.fit(train_X, train_y)

current_features = features[-1:].reshape(1, -1)
score = model.predict_proba(current_features)[0][1]

if score > threshold:
    strategy.entry("ML Long", strategy.LONG)
elif score < (1 - threshold):
    strategy.close("ML Long")

plot(score * 100, "ML Score", color="cyan")
hline(threshold * 100, "Buy Threshold", color="green", linestyle="dashed")
hline((1 - threshold) * 100, "Sell Threshold", color="red", linestyle="dashed")
