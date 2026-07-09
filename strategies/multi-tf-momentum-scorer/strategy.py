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
entry_thresh = input.float(0.35, "Entry Threshold", minval=0.1, maxval=0.8)
exit_thresh = input.float(0.1, "Exit Threshold", minval=0.0, maxval=0.5)
min_bars = input.int(10, "Min Bars Between Trades", minval=1, maxval=50)
smooth_len = input.int(5, "Score Smoothing", minval=1, maxval=20)

n = len(close)
close_np = np.asarray(close).astype(np.float64)

# --- Generate synthetic timeframe lookback periods ---
tf_periods = [int(base_period * (tf_multiplier ** i)) for i in range(num_timeframes)]
tf_periods = [p for p in tf_periods if p < n // 2]
num_tf = len(tf_periods)

def resample_close(data, period):
    indices = np.arange(0, len(data), period)
    sampled = data[indices]
    return np.interp(np.arange(len(data)), indices, sampled)

def ema_smooth(arr, length):
    if length <= 1:
        return arr
    out = np.copy(arr)
    alpha = 2.0 / (length + 1)
    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]
    return out

resampled = [resample_close(close_np, p) for p in tf_periods]

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

def calc_roc(source, length):
    shifted = np.roll(source, length)
    shifted[:length] = source[:length]
    return np.where(shifted != 0, (source - shifted) / np.abs(shifted) * 100, 0.0)

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
    raw_score = np.average([rsi_score, roc_score, trend], axis=0, weights=[0.35, 0.35, 0.30])
    tf_scores[idx] = ema_smooth(raw_score, smooth_len + idx * 2)
    tf_weights[idx] = np.log(period + 1)

tf_weights = tf_weights / np.sum(tf_weights)

# --- Composite Multi-TF Score ---
composite = np.zeros(n)
for idx in range(num_tf):
    composite += tf_weights[idx] * tf_scores[idx]
composite = ema_smooth(composite, smooth_len)

# --- Consensus ---
directions = np.sign(tf_scores)
consensus_up = np.sum(directions > 0, axis=0) / num_tf
consensus_down = np.sum(directions < 0, axis=0) / num_tf
confidence = np.abs(composite) * np.maximum(consensus_up, consensus_down)

# --- Signals ---
strong_bull = (composite > entry_thresh) & (consensus_up >= consensus_thresh)
strong_bear = (composite < -entry_thresh) & (consensus_down >= consensus_thresh)

prev_bull = np.roll(strong_bull, 1)
prev_bear = np.roll(strong_bear, 1)
prev_bull[0] = False
prev_bear[0] = False

long_entry = strong_bull & ~prev_bull
short_entry = strong_bear & ~prev_bear
long_exit = (composite < exit_thresh) & prev_bull
short_exit = (composite > -exit_thresh) & prev_bear

# --- Trade execution (tracks actual entries for markers) ---
in_position = None
last_trade_bar = -min_bars
actual_buy = np.full(n, np.nan)
actual_sell = np.full(n, np.nan)
actual_exit = np.full(n, np.nan)

for i in range(n):
    strategy.set_bar_index(i)
    if long_entry[i] and in_position != "long" and (i - last_trade_bar) >= min_bars:
        if in_position == "short":
            strategy.close("Short")
        strategy.entry("Long", strategy.LONG)
        in_position = "long"
        last_trade_bar = i
        actual_buy[i] = composite[i]
    elif short_entry[i] and in_position != "short" and (i - last_trade_bar) >= min_bars:
        if in_position == "long":
            strategy.close("Long")
        strategy.entry("Short", strategy.SHORT)
        in_position = "short"
        last_trade_bar = i
        actual_sell[i] = composite[i]
    elif long_exit[i] and in_position == "long":
        strategy.close("Long")
        in_position = None
        actual_exit[i] = composite[i]
    elif short_exit[i] and in_position == "short":
        strategy.close("Short")
        in_position = None
        actual_exit[i] = composite[i]

# === PLOTS ===

# TF score lines (smoothed, spread out by increasing EMA per TF)
tf_colors = ["#69E1FB", "#26a69a", "#ff9800", "#ab47bc", "#ef5350",
             "#42a5f5", "#66bb6a", "#ffa726"]
tf_names = []
for idx in range(num_tf):
    period = tf_periods[idx]
    color = tf_colors[idx % len(tf_colors)]
    name = f"{period}-bar"
    tf_names.append(name)
    plot(tf_scores[idx], title=name, color=color, linewidth=1)

# Composite (thick white line)
plot(composite, title="Composite", color="#e0e0e0", linewidth=2)

# Threshold lines
hline(entry_thresh, title="Entry Threshold", color="rgba(0,230,118,0.5)", linestyle="dashed")
hline(-entry_thresh, title="Short Threshold", color="rgba(239,83,80,0.5)", linestyle="dashed")
hline(0, title="Zero", color="rgba(255,255,255,0.2)")

# Consensus shading
bull_bg = [("rgba(76,175,80,0.12)" if strong_bull[i] else None) for i in range(n)]
bear_bg = [("rgba(244,67,54,0.12)" if strong_bear[i] else None) for i in range(n)]
bgcolor(bull_bg, title="Bull Zone")
bgcolor(bear_bg, title="Bear Zone")

# Signal markers — only on ACTUAL trades, not all transitions
plotshape(actual_buy, title="Buy", style="triangleup", location="absolute",
          color="#00e676", text="BUY", textcolor="#00e676", size="small")
plotshape(actual_sell, title="Sell", style="triangledown", location="absolute",
          color="#ef5350", text="SELL", textcolor="#ef5350", size="small")
plotshape(actual_exit, title="Exit", style="xcross", location="absolute",
          color="#ff9800", text="EXIT", textcolor="#ff9800", size="tiny")

# Consensus count labels at trade entries
for i in range(n):
    if not np.isnan(actual_buy[i]):
        bull_count = int(np.sum(directions[:, i] > 0))
        conf_pct = int(confidence[i] * 100)
        label.new(x=i, y=float(composite[i]) + 0.08,
                  text=f"{bull_count}/{num_tf} Bullish ({conf_pct}%)",
                  style=label.style_label_down,
                  color="rgba(76,175,80,0.3)",
                  textcolor="#66bb6a", size="tiny")
    elif not np.isnan(actual_sell[i]):
        bear_count = int(np.sum(directions[:, i] < 0))
        conf_pct = int(confidence[i] * 100)
        label.new(x=i, y=float(composite[i]) - 0.08,
                  text=f"{bear_count}/{num_tf} Bearish ({conf_pct}%)",
                  style=label.style_label_up,
                  color="rgba(239,83,80,0.3)",
                  textcolor="#ef5350", size="tiny")
