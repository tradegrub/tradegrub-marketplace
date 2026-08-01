from tg_scripting import *
import numpy as np
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

indicator("Gradient Boosted Trend Classifier", overlay=False)

# --- Inputs ---
atr_len = input.int(14, "ATR Length", minval=2, maxval=50)
vol_len = input.int(20, "Volume SMA Length", minval=5, maxval=100)
train_pct = input.float(0.7, "Training Split", minval=0.3, maxval=0.9, step=0.05)
threshold = input.float(0.02, "Neutral Threshold", minval=0.001, maxval=0.1, step=0.005)
n_estimators = input.int(100, "Num Estimators", minval=10, maxval=500)
show_labels = input.bool(True, "Show Regime Labels")
label_cooldown = input.int(15, "Label Cooldown", minval=1, maxval=50)

# --- Price and volume arrays ---
c = np.array(close, dtype=np.float64)
h = np.array(high, dtype=np.float64)
l = np.array(low, dtype=np.float64)
v = np.array(volume, dtype=np.float64)
n = len(c)

# --- Feature engineering ---
atr_vals = np.array(ta.atr(high, low, close, atr_len), dtype=np.float64)
vol_sma = np.array(ta.sma(volume, vol_len), dtype=np.float64)

# Multi-period returns
ret5 = np.full(n, np.nan)
ret10 = np.full(n, np.nan)
ret20 = np.full(n, np.nan)
for i in range(20, n):
    ret5[i] = (c[i] - c[i - 5]) / c[i - 5]
    ret10[i] = (c[i] - c[i - 10]) / c[i - 10]
    ret20[i] = (c[i] - c[i - 20]) / c[i - 20]

# ATR ratio
atr_ratio = np.full(n, np.nan)
for i in range(n):
    if c[i] > 0 and not np.isnan(atr_vals[i]):
        atr_ratio[i] = atr_vals[i] / c[i]

# Volume SMA ratio
vol_ratio = np.full(n, np.nan)
for i in range(n):
    if not np.isnan(vol_sma[i]) and vol_sma[i] > 0:
        vol_ratio[i] = v[i] / vol_sma[i]

# RSI-like momentum (gains vs losses over 14 bars)
momentum = np.full(n, np.nan)
for i in range(14, n):
    changes = np.diff(c[i - 14:i + 1])
    gains = np.sum(changes[changes > 0])
    losses = -np.sum(changes[changes < 0])
    if losses > 0:
        momentum[i] = gains / losses
    else:
        momentum[i] = 10.0  # cap when no losses

# --- Build feature matrix ---
features = np.column_stack([ret5, ret10, ret20, atr_ratio, vol_ratio, momentum])
feature_names = ["ret5", "ret10", "ret20", "atr_ratio", "vol_ratio", "momentum"]

# Find valid rows (no NaN in any feature)
valid_mask = ~np.any(np.isnan(features), axis=1)

# --- Labels from future returns ---
labels = np.full(n, np.nan)
for i in range(n - 10):
    fwd_ret = (c[i + 10] - c[i]) / c[i]
    if fwd_ret > threshold:
        labels[i] = 2  # bullish
    elif fwd_ret < -threshold:
        labels[i] = 0  # bearish
    else:
        labels[i] = 1  # neutral

label_mask = ~np.isnan(labels)
full_mask = valid_mask & label_mask
valid_idx = np.where(full_mask)[0]

# --- Output arrays ---
bull_prob = np.full(n, np.nan)
bear_prob = np.full(n, np.nan)
confidence = np.full(n, np.nan)

feat_imp = np.zeros(len(feature_names))

if len(valid_idx) > 50 and HAS_LIGHTGBM:
    X_valid = features[valid_idx]
    y_valid = labels[valid_idx].astype(int)

    split = int(len(valid_idx) * train_pct)
    train_idx = valid_idx[:split]
    X_train = features[train_idx]
    y_train = labels[train_idx].astype(int)

    model = lgb.LGBMClassifier(
        n_estimators=n_estimators,
        max_depth=5,
        learning_rate=0.05,
        num_leaves=31,
        min_child_samples=10,
        verbosity=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    feat_imp = model.feature_importances_.astype(float)

    pred_idx = np.where(valid_mask)[0]
    X_pred = features[pred_idx]
    probs = model.predict_proba(X_pred)
    class_list = list(model.classes_)
    bear_ci = class_list.index(0) if 0 in class_list else None
    neut_ci = class_list.index(1) if 1 in class_list else None
    bull_ci = class_list.index(2) if 2 in class_list else None

    for j, idx in enumerate(pred_idx):
        bp = probs[j, bull_ci] if bull_ci is not None else 0.0
        brp = probs[j, bear_ci] if bear_ci is not None else 0.0
        bull_prob[idx] = bp
        bear_prob[idx] = brp
        sorted_p = np.sort(probs[j])[::-1]
        confidence[idx] = sorted_p[0] - sorted_p[1] if len(sorted_p) > 1 else sorted_p[0]
elif len(valid_idx) > 50:
    pred_idx = np.where(valid_mask)[0]
    for idx in pred_idx:
        r5 = features[idx, 0]
        mom = features[idx, 5]
        bull_prob[idx] = max(0.0, min(1.0, 0.5 + r5 * 5 + (mom - 1.0) * 0.1))
        bear_prob[idx] = 1.0 - bull_prob[idx]
        confidence[idx] = abs(bull_prob[idx] - 0.5) * 2

# --- Plotting ---
plot(bull_prob, title="Bullish Prob", color="#4CAF50")
plot(bear_prob, title="Bearish Prob", color="#ef5350")
plot(confidence, title="Confidence", color="#FF9800")
hline(0.5, title="Midline", color="#9E9E9E", linestyle="dashed")

# Background color for high-confidence regimes
bull_bg = np.array([not np.isnan(bull_prob[i]) and not np.isnan(confidence[i]) and bull_prob[i] > 0.5 and confidence[i] > 0.3 for i in range(n)])
bear_bg = np.array([not np.isnan(bear_prob[i]) and not np.isnan(confidence[i]) and bear_prob[i] > 0.5 and confidence[i] > 0.3 for i in range(n)])
bgcolor(bull_bg, color="rgba(76,175,80,0.1)")
bgcolor(bear_bg, color="rgba(239,83,80,0.1)")

# Regime change labels with cooldown
if show_labels:
    last_label_bar = -label_cooldown
    prev_regime = None
    for i in range(n):
        if np.isnan(bull_prob[i]) or np.isnan(bear_prob[i]):
            continue
        if bull_prob[i] > 0.5 and confidence[i] > 0.25:
            regime = "bull"
        elif bear_prob[i] > 0.5 and confidence[i] > 0.25:
            regime = "bear"
        else:
            regime = "neutral"
        if regime != prev_regime and (i - last_label_bar) >= label_cooldown:
            if regime == "bull":
                label.new(x=i, y=float(bull_prob[i]), text="Bullish", style=label.style_label_up, color="#4CAF50", textcolor="#FFFFFF", size="small")
            elif regime == "bear":
                label.new(x=i, y=float(bear_prob[i]), text="Bearish", style=label.style_label_down, color="#ef5350", textcolor="#FFFFFF", size="small")
            last_label_bar = i
        prev_regime = regime

