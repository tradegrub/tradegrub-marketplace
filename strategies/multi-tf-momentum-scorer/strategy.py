from tg_scripting import *
import numpy as np

indicator("Multi-TF Momentum Scorer", overlay=True)

# Inputs
base_period = input.int(5, "Base Period", minval=2, maxval=20)
num_timeframes = input.int(5, "Number of Timeframes", minval=2, maxval=8)
tf_multiplier = input.float(2.0, "Timeframe Multiplier", minval=1.5, maxval=4.0)
consensus_thresh = input.float(0.7, "Consensus Threshold", minval=0.3, maxval=1.0)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
roc_len = input.int(10, "ROC Length", minval=3, maxval=30)
use_sizing = input.bool(True, "Confidence-Weighted Sizing")
max_risk = input.float(2.0, "Max Risk %", minval=0.5, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

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
consensus = np.maximum(consensus_up, consensus_down)

# --- Confidence-weighted position sizing ---
confidence = np.abs(composite) * consensus
position_pct = np.clip(confidence * max_risk, 0, max_risk) if use_sizing else np.full(n, max_risk)

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

atr = ta.atr(high, low, close, 14)
last_signal_idx = -100
cooldown = 20

for i in range(n):
    if long_entry[i]:
        strategy.entry("Long", strategy.LONG)
        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(low_np[i]),
                    text="BUY",
                    style=label.style_label_up,
                    color="#00e676",
                    textcolor="#000000",
                    size="small"
                )
            if show_levels:
                entry_price = float(close_np[i])
                atr_val = float(atr[i]) if not np.isnan(float(atr[i])) else entry_price * 0.02
                sl_price = entry_price - atr_val * 2.0
                tp_price = entry_price + atr_val * 4.0
                end_bar = min(i + 30, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                        border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.05)")

    elif short_entry[i]:
        strategy.entry("Short", strategy.SHORT)
        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(
                    x=i, y=float(high_np[i]),
                    text="EXIT",
                    style=label.style_label_down,
                    color="#ef5350",
                    textcolor="#ffffff",
                    size="small"
                )
            if show_levels:
                entry_price = float(close_np[i])
                atr_val = float(atr[i]) if not np.isnan(float(atr[i])) else entry_price * 0.02
                sl_price = entry_price + atr_val * 2.0
                tp_price = entry_price - atr_val * 4.0
                end_bar = min(i + 30, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                        border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.05)")

    elif long_exit[i]:
        strategy.close("Long")
        if show_labels and (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            label.new(
                x=i, y=float(high_np[i]),
                text="EXIT",
                style=label.style_label_down,
                color="#ff9800",
                textcolor="#000000",
                size="small"
            )
    elif short_exit[i]:
        strategy.close("Short")
        if show_labels and (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            label.new(
                x=i, y=float(low_np[i]),
                text="EXIT",
                style=label.style_label_up,
                color="#ff9800",
                textcolor="#000000",
                size="small"
            )

# --- Sub-pane: individual TF score lines (overlay=False forces sub-pane) ---
tf_colors = ["#69E1FB", "#26a69a", "#ff9800", "#ab47bc", "#ef5350",
             "#42a5f5", "#66bb6a", "#ffa726"]

for idx in range(num_tf):
    period = tf_periods[idx]
    color = tf_colors[idx % len(tf_colors)]
    plot(tf_scores[idx], title=f"TF {period}-bar", color=color, linewidth=1, overlay=False)

# Composite score (thicker white line in sub-pane)
plot(composite, title="Composite", color="#e0e0e0", linewidth=2, overlay=False)

# Threshold lines in sub-pane
hline(consensus_thresh, title="Bull Threshold", color="rgba(0,230,118,0.4)", linestyle="dashed", overlay=False)
hline(-consensus_thresh, title="Bear Threshold", color="rgba(239,83,80,0.4)", linestyle="dashed", overlay=False)
hline(0, title="Zero", color="rgba(255,255,255,0.15)", overlay=False)

# Shade consensus zones on price chart
bull_bg = [("rgba(76,175,80,0.08)" if strong_bull[i] else None) for i in range(n)]
bear_bg = [("rgba(244,67,54,0.08)" if strong_bear[i] else None) for i in range(n)]
bgcolor(bull_bg, title="Bull Zone")
bgcolor(bear_bg, title="Bear Zone")
