from tg_scripting import *
import numpy as np

lookback = input.int(100, "Lookback", minval=20, maxval=500)

src_close = np.array(close, dtype=float)
src_high = np.array(high, dtype=float)
src_low = np.array(low, dtype=float)
src_vol = np.array(volume, dtype=float)
n = len(src_close)

# RSI calculation
def calc_rsi(data, period=14):
    delta = np.diff(data, prepend=data[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.empty(len(data))
    avg_loss = np.empty(len(data))
    avg_gain[0] = 0.0
    avg_loss[0] = 0.0
    for i in range(1, min(period + 1, len(data))):
        avg_gain[i] = np.mean(gain[1:i + 1])
        avg_loss[i] = np.mean(loss[1:i + 1])
    alpha = 1.0 / period
    for i in range(period + 1, len(data)):
        avg_gain[i] = avg_gain[i - 1] * (1 - alpha) + gain[i] * alpha
        avg_loss[i] = avg_loss[i - 1] * (1 - alpha) + loss[i] * alpha
    rs = np.where(avg_loss > 0, avg_gain / avg_loss, 100.0)
    return 100.0 - 100.0 / (1.0 + rs)

# ATR calculation
def calc_atr(h, l, c, period=14):
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    atr = np.empty(len(c))
    atr[0] = tr[0]
    for i in range(1, len(c)):
        atr[i] = atr[i - 1] * (period - 1) / period + tr[i] / period
    return atr

rsi = calc_rsi(src_close) / 100.0
atr = calc_atr(src_high, src_low, src_close)
atr_norm = np.where(src_close > 0, atr / src_close, 0.0)

vol_sma = np.empty(n)
for i in range(n):
    start = max(0, i - 19)
    vol_sma[i] = np.mean(src_vol[start:i + 1])
vol_ratio = np.where(vol_sma > 0, src_vol / vol_sma, 1.0)

price_range = np.empty(n)
for i in range(n):
    start = max(0, i - 19)
    hi = np.max(src_high[start:i + 1])
    lo = np.min(src_low[start:i + 1])
    rng = hi - lo
    price_range[i] = (src_close[i] - lo) / rng if rng > 0 else 0.5

# Future returns for each bar (1-bar forward return)
future_ret = np.zeros(n)
future_ret[:-1] = (src_close[1:] - src_close[:-1]) / np.where(src_close[:-1] > 0, src_close[:-1], 1.0)

# Attention-based prediction
prediction = np.zeros(n)

for i in range(lookback, n):
    current_feat = np.array([rsi[i], atr_norm[i], vol_ratio[i], price_range[i]])
    feat_norm = np.linalg.norm(current_feat)
    if feat_norm < 1e-10:
        continue

    start = i - lookback
    past_feats = np.column_stack([
        rsi[start:i],
        atr_norm[start:i],
        vol_ratio[start:i],
        price_range[start:i]
    ])

    # Dot product similarity
    similarities = past_feats @ current_feat

    # Softmax
    sim_max = np.max(similarities)
    exp_sim = np.exp(similarities - sim_max)
    weights = exp_sim / np.sum(exp_sim)

    # Weighted average of future returns
    past_returns = future_ret[start:i]
    prediction[i] = np.sum(weights * past_returns) * 10000  # Scale to basis points

# Clamp to -100..100
prediction = np.clip(prediction, -100, 100)

plot(prediction, title="Attention Score", color="#e040fb")
hline(0, title="Zero", color="#555555")
hline(50, title="Strong Bull", color="#00e676")
hline(-50, title="Strong Bear", color="#ff1744")

bgcolor(prediction > 50, color="rgba(0,230,118,0.1)")
bgcolor(prediction < -50, color="rgba(255,23,68,0.1)")
