from tg_scripting import *

# Inputs
base_period = input.int(5, "Base Period", minval=2, maxval=20)
num_timeframes = input.int(5, "Number of Timeframes", minval=2, maxval=8)
tf_multiplier = input.float(2.0, "Timeframe Multiplier", minval=1.5, maxval=4.0)
consensus_thresh = input.float(0.7, "Consensus Threshold", minval=0.3, maxval=1.0)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
roc_len = input.int(10, "ROC Length", minval=3, maxval=30)
use_sizing = input.bool(True, "Confidence-Weighted Sizing")
max_risk = input.float(2.0, "Max Risk %", minval=0.5, maxval=5.0)

n = len(close)

# --- Generate synthetic timeframe lookback periods ---
tf_periods = [int(base_period * (tf_multiplier ** i)) for i in range(num_timeframes)]
tf_periods = [p for p in tf_periods if p < n // 2]
num_tf = len(tf_periods)

# --- Resample close data at each timeframe resolution ---
def resample_close(data, period):
    """Downsample by taking every period-th bar, then interpolate back."""
    indices = np.arange(0, len(data), period)
    sampled = data[indices]
    # Interpolate back to full length
    full = np.interp(np.arange(len(data)), indices, sampled)
    return full

resampled = [resample_close(close, p) for p in tf_periods]

# --- Multi-period RSI calculation (vectorized) ---
def calc_rsi(source, length):
    delta = np.diff(source, prepend=source[0])
    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)
    # Exponential moving average of gains/losses
    avg_gain = np.zeros(len(source))
    avg_loss = np.zeros(len(source))
    avg_gain[length] = np.mean(gains[1:length + 1])
    avg_loss[length] = np.mean(losses[1:length + 1])
    alpha = 1.0 / length
    for i in range(length + 1, len(source)):
        avg_gain[i] = avg_gain[i - 1] * (1 - alpha) + gains[i] * alpha
        avg_loss[i] = avg_loss[i - 1] * (1 - alpha) + losses[i] * alpha
    rs = np.where(avg_loss > 0, avg_gain / avg_loss, 100.0)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi[:length] = 50.0
    return rsi

# --- Rate of Change (vectorized) ---
def calc_roc(source, length):
    shifted = np.roll(source, length)
    shifted[:length] = source[:length]
    roc = np.where(shifted != 0, (source - shifted) / np.abs(shifted) * 100, 0.0)
    return roc

# --- Trend alignment score using linear regression slope ---
def calc_trend_score(source, length):
    scores = np.zeros(len(source))
    x = np.arange(length, dtype=float)
    x_mean = np.mean(x)
    x_var = np.sum((x - x_mean) ** 2)
    for i in range(length, len(source)):
        window = source[i - length:i]
        y_mean = np.mean(window)
        slope = np.sum((x - x_mean) * (window - y_mean)) / x_var
        # Normalize slope by price level
        scores[i] = slope / (y_mean + 1e-10) * length
    return np.clip(scores, -1.0, 1.0)

# --- Score each timeframe ---
tf_scores = np.zeros((num_tf, n))
tf_weights = np.zeros(num_tf)

for idx, (period, resampled_data) in enumerate(zip(tf_periods, resampled)):
    # RSI momentum: map 0-100 to -1 to +1
    rsi = calc_rsi(resampled_data, rsi_len)
    rsi_score = (rsi - 50.0) / 50.0

    # ROC momentum: sign and magnitude
    roc = calc_roc(resampled_data, min(roc_len, period))
    roc_score = np.clip(roc / 5.0, -1.0, 1.0)

    # Trend alignment
    trend = calc_trend_score(resampled_data, min(period, 30))

    # Composite score for this timeframe
    tf_scores[idx] = np.average(
        [rsi_score, roc_score, trend],
        axis=0,
        weights=[0.35, 0.35, 0.30]
    )

    # Higher timeframes get more weight (log scale)
    tf_weights[idx] = np.log(period + 1)

# Normalize weights
tf_weights = tf_weights / np.sum(tf_weights)

# --- Composite Multi-TF Score ---
composite = np.zeros(n)
for idx in range(num_tf):
    composite += tf_weights[idx] * tf_scores[idx]

# --- Consensus: how many timeframes agree on direction ---
directions = np.sign(tf_scores)  # (num_tf, n)
consensus_up = np.sum(directions > 0, axis=0) / num_tf
consensus_down = np.sum(directions < 0, axis=0) / num_tf
consensus = np.maximum(consensus_up, consensus_down)

# --- Confidence-weighted position sizing ---
confidence = np.abs(composite) * consensus
position_pct = np.clip(confidence * max_risk, 0, max_risk) if use_sizing else np.full(n, max_risk)

# --- Entry/Exit Signals ---
strong_bull = (composite > 0.2) & (consensus_up >= consensus_thresh)
strong_bear = (composite < -0.2) & (consensus_down >= consensus_thresh)

# Detect signal transitions
prev_bull = np.roll(strong_bull, 1)
prev_bear = np.roll(strong_bear, 1)
prev_bull[0] = False
prev_bear[0] = False

long_entry = strong_bull & ~prev_bull
short_entry = strong_bear & ~prev_bear
long_exit = ~strong_bull & prev_bull
short_exit = ~strong_bear & prev_bear

for i in range(n):
    if long_entry[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_entry[i]:
        strategy.entry("Short", strategy.SHORT)
    elif long_exit[i]:
        strategy.close("Long")
    elif short_exit[i]:
        strategy.close("Short")

# --- Plots ---
plot(composite, title="Composite Score", color="#2196F3")
plot(consensus_up, title="Bull Consensus", color="rgba(76,175,80,0.5)")
plot(consensus_down, title="Bear Consensus", color="rgba(244,67,54,0.5)")
hline(0, title="Zero Line", color="gray")
hline(consensus_thresh, title="Consensus Threshold", color="green")

plot(confidence, title="Confidence", color="#FF9800")
plot(position_pct, title="Position %", color="#9C27B0")

bgcolor(strong_bull, color="rgba(76,175,80,0.08)")
bgcolor(strong_bear, color="rgba(244,67,54,0.08)")

plotarrow(np.where(long_entry, 1, np.where(short_entry, -1, 0)), title="Signals", colorup="green", colordown="red")
