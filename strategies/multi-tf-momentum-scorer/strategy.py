from tg_scripting import *
import numpy as np

indicator("Multi-TF Momentum Scorer", overlay=False)

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
close_np = np.asarray(close).astype(np.float64)
high_np = np.asarray(high).astype(np.float64)
low_np = np.asarray(low).astype(np.float64)

# --- Generate synthetic timeframe lookback periods ---
tf_periods = [int(base_period * (tf_multiplier ** i)) for i in range(num_timeframes)]
tf_periods = [p for p in tf_periods if p < n // 2]
num_tf = len(tf_periods)

# --- Resample close data at each timeframe resolution ---
def resample_close(data, period):
    indices = np.arange(0, len(data), period)
    sampled = data[indices]
    full = np.interp(np.arange(len(data)), indices, sampled)
    return full

resampled = [resample_close(close_np, p) for p in tf_periods]

# --- Multi-period RSI calculation (vectorized) ---
def calc_rsi(source, length):
    delta = np.diff(source, prepend=source[0])
    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)
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
        scores[i] = slope / (y_mean + 1e-10) * length
    return np.clip(scores, -1.0, 1.0)

# --- Score each timeframe ---
tf_scores = np.zeros((num_tf, n))
tf_weights = np.zeros(num_tf)

for idx, (period, resampled_data) in enumerate(zip(tf_periods, resampled)):
    rsi = calc_rsi(resampled_data, rsi_len)
    rsi_score = (rsi - 50.0) / 50.0
    roc = calc_roc(resampled_data, min(roc_len, period))
    roc_score = np.clip(roc / 5.0, -1.0, 1.0)
    trend = calc_trend_score(resampled_data, min(period, 30))
    tf_scores[idx] = np.average(
        [rsi_score, roc_score, trend],
        axis=0,
        weights=[0.35, 0.35, 0.30]
    )
    tf_weights[idx] = np.log(period + 1)

tf_weights = tf_weights / np.sum(tf_weights)

# --- Composite Multi-TF Score ---
composite = np.zeros(n)
for idx in range(num_tf):
    composite += tf_weights[idx] * tf_scores[idx]

# --- Consensus: how many timeframes agree on direction ---
directions = np.sign(tf_scores)
consensus_up = np.sum(directions > 0, axis=0) / num_tf
consensus_down = np.sum(directions < 0, axis=0) / num_tf

# --- Entry/Exit Signals ---
strong_bull = (composite > 0.2) & (consensus_up >= consensus_thresh)
strong_bear = (composite < -0.2) & (consensus_down >= consensus_thresh)

prev_bull = np.roll(strong_bull, 1)
prev_bear = np.roll(strong_bear, 1)
prev_bull[0] = False
prev_bear[0] = False

long_entry = strong_bull & ~prev_bull
short_entry = strong_bear & ~prev_bear
long_exit = ~strong_bull & prev_bull
short_exit = ~strong_bear & prev_bear

in_position = None
for i in range(n):
    strategy.set_bar_index(i)
    if long_entry[i] and in_position != "long":
        if in_position == "short":
            strategy.close("Short")
        strategy.entry("Long", strategy.LONG)
        in_position = "long"
    elif short_entry[i] and in_position != "short":
        if in_position == "long":
            strategy.close("Long")
        strategy.entry("Short", strategy.SHORT)
        in_position = "short"
    elif long_exit[i] and in_position == "long":
        strategy.close("Long")
        in_position = None
    elif short_exit[i] and in_position == "short":
        strategy.close("Short")
        in_position = None

# --- Sub-pane plots: individual TF score lines ---
tf_colors = ["#69E1FB", "#26a69a", "#ff9800", "#ab47bc", "#ef5350",
             "#42a5f5", "#66bb6a", "#ffa726"]

for idx in range(num_tf):
    period = tf_periods[idx]
    color = tf_colors[idx % len(tf_colors)]
    plot(tf_scores[idx], title=f"TF {period}-bar", color=color, linewidth=1)

# Composite score (thicker white line)
plot(composite, title="Composite", color="#e0e0e0", linewidth=2)

# Threshold lines
hline(consensus_thresh, title="Bull Threshold", color="rgba(0,230,118,0.4)", linestyle="dashed")
hline(-consensus_thresh, title="Bear Threshold", color="rgba(239,83,80,0.4)", linestyle="dashed")
hline(0, title="Zero", color="rgba(255,255,255,0.15)")

# Shade consensus zones
bull_bg = [("rgba(76,175,80,0.12)" if strong_bull[i] else None) for i in range(n)]
bear_bg = [("rgba(244,67,54,0.12)" if strong_bear[i] else None) for i in range(n)]
bgcolor(bull_bg, title="Bull Zone")
bgcolor(bear_bg, title="Bear Zone")

# Signal markers using plotshape
buy_sig = np.where(long_entry, composite, np.nan)
sell_sig = np.where(short_entry, composite, np.nan)
exit_bull = np.where(long_exit, composite, np.nan)
exit_bear = np.where(short_exit, composite, np.nan)

plotshape(buy_sig, title="Buy", style="triangleup", location="absolute",
          color="#00e676", text="BUY", textcolor="#00e676", size="small")
plotshape(sell_sig, title="Sell", style="triangledown", location="absolute",
          color="#ef5350", text="SELL", textcolor="#ef5350", size="small")
plotshape(exit_bull, title="Exit Long", style="xcross", location="absolute",
          color="#ff9800", text="EXIT", textcolor="#ff9800", size="tiny")
plotshape(exit_bear, title="Exit Short", style="xcross", location="absolute",
          color="#ff9800", text="EXIT", textcolor="#ff9800", size="tiny")
