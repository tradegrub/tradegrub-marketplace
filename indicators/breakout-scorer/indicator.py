from tg_scripting import *
import numpy as np

indicator("Breakout Probability Scorer", overlay=False)

# --- Inputs ---
atr_len = input.int(14, "ATR Length", minval=1)
lookback = input.int(20, "Lookback Period", minval=5)
breakout_pct = input.float(2.0, "Breakout Threshold %", minval=0.1, step=0.1)
n_estimators = input.int(100, "XGB Estimators", minval=10)
score_threshold = input.float(0.7, "Score Threshold", minval=0.0, maxval=1.0, step=0.05)
show_labels = input.bool(True, "Show Labels")
label_cooldown = input.int(10, "Label Cooldown Bars", minval=1)

# --- Feature Engineering ---
atr_val = ta.atr(high, low, close, atr_len)
sma_vol = ta.sma(volume, lookback)
highest_high = ta.highest(high, lookback)
lowest_low = ta.lowest(low, lookback)

# Consolidation tightness: current ATR relative to rolling max ATR
rolling_max_atr = ta.highest(atr_val, lookback)
consolidation_tightness = np.where(
    rolling_max_atr > 0,
    1.0 - (atr_val / rolling_max_atr),
    0.0
)

# Volume buildup: current volume relative to average
volume_ratio = np.where(
    sma_vol > 0,
    volume / sma_vol,
    1.0
)

# Proximity to recent high (0 = at low, 1 = at high)
range_span = highest_high - lowest_low
prox_high = np.where(
    range_span > 0,
    (close - lowest_low) / range_span,
    0.5
)

# Proximity to recent low (inverse)
prox_low = np.where(
    range_span > 0,
    (highest_high - close) / range_span,
    0.5
)

# Momentum: rate of change over lookback
close_arr = np.array(close, dtype=np.float64)
roc = np.zeros(len(close_arr))
for i in range(lookback, len(close_arr)):
    if close_arr[i - lookback] != 0:
        roc[i] = (close_arr[i] - close_arr[i - lookback]) / close_arr[i - lookback]

# --- Label Generation (breakout events) ---
# A breakout is when price moves > breakout_pct% beyond the consolidation range
# within the next N bars (forward-looking for training)
n_bars_forward = lookback
breakout_labels = np.zeros(len(close))
for i in range(len(close) - n_bars_forward):
    future_high = np.max(high[i + 1:i + 1 + n_bars_forward])
    future_low = np.min(low[i + 1:i + 1 + n_bars_forward])
    upper_bound = highest_high[i]
    lower_bound = lowest_low[i]
    if range_span[i] > 0:
        upside_move = (future_high - upper_bound) / upper_bound * 100
        downside_move = (lower_bound - future_low) / lower_bound * 100
        if upside_move > breakout_pct or downside_move > breakout_pct:
            breakout_labels[i] = 1.0

# --- Build Feature Matrix ---
features = np.column_stack([
    consolidation_tightness,
    volume_ratio,
    prox_high,
    prox_low,
    roc
])

# Replace NaN/Inf with 0
features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

# --- Train XGBoost Model ---
try:
    from xgboost import XGBClassifier

    # Use data up to a training cutoff (leave last portion for live scoring)
    train_mask = np.isfinite(features).all(axis=1) & (np.arange(len(close)) >= lookback)
    train_end = max(int(len(close) * 0.8), lookback + 50)

    train_idx = train_mask.copy()
    train_idx[train_end:] = False

    if np.sum(train_idx) > 50 and np.sum(breakout_labels[train_idx]) > 5:
        model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0
        )
        model.fit(features[train_idx], breakout_labels[train_idx])

        # Score all bars
        breakout_score = model.predict_proba(features)[:, 1]
    else:
        # Fallback: simple heuristic score
        breakout_score = (
            consolidation_tightness * 0.35 +
            np.clip(volume_ratio / 3.0, 0, 1) * 0.25 +
            prox_high * 0.2 +
            np.abs(roc) * 0.2
        )
except ImportError:
    # Fallback if xgboost not available
    breakout_score = (
        consolidation_tightness * 0.35 +
        np.clip(volume_ratio / 3.0, 0, 1) * 0.25 +
        prox_high * 0.2 +
        np.abs(roc) * 0.2
    )

breakout_score = np.clip(breakout_score, 0.0, 1.0)

# --- Direction Bias ---
direction_bias = np.where(prox_high > 0.6, "Bullish",
                 np.where(prox_low > 0.6, "Bearish", "Neutral"))

# --- Plotting ---
plot(breakout_score, title="Breakout Score", color="#00BCD4", linewidth=2)
hline(float(score_threshold), title="Threshold", color="#FF9800", linestyle="dashed")
hline(0.0, title="Zero", color="rgba(158,158,158,0.2)")
hline(1.0, title="One", color="rgba(158,158,158,0.2)")

# Background highlight when score exceeds threshold
alert_active = breakout_score > score_threshold
bgcolor(alert_active, color="rgba(76,175,80,0.15)")

# Alert shapes
plotshape(alert_active, title="Breakout Alert", style="triangleup", location="bottom", color="#00e676")

# Labels with cooldown
if show_labels:
    bars_since_label = label_cooldown + 1
    for i in range(len(close)):
        bars_since_label += 1
        if alert_active[i] and bars_since_label > label_cooldown:
            bias = direction_bias[i] if isinstance(direction_bias[i], str) else str(direction_bias[i])
            label.new(
                x=i, y=float(breakout_score[i]),
                text=f"Breakout\n{bias}\n{breakout_score[i]:.2f}",
                style=label.style_label_up,
                color="rgba(76,175,80,0.8)",
                textcolor="#FFFFFF",
                size="small"
            )
            bars_since_label = 0

# Alert condition
alertcondition(alert_active, title="Breakout Score Alert",
               message="XGBoost breakout score exceeded threshold")
