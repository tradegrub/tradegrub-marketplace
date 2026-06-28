from tg_scripting import *
import numpy as np

# --- Inputs ---
atr_min = input.int(5, "Min ATR Length", minval=2, maxval=50)
atr_max = input.int(25, "Max ATR Length", minval=5, maxval=100)
atr_step = input.int(5, "ATR Length Step", minval=1, maxval=10)
mult_min = input.float(1.0, "Min Multiplier", minval=0.5, maxval=5.0)
mult_max = input.float(4.0, "Max Multiplier", minval=1.0, maxval=10.0)
mult_step = input.float(0.5, "Multiplier Step", minval=0.1, maxval=2.0)
score_lookback = input.int(50, "Scoring Lookback", minval=10, maxval=200)
show_optimal = input.bool(True, "Show Optimal Supertrend")
show_consensus = input.bool(True, "Show Consensus Direction")
signal_weight = input.float(0.4, "Signal Change Weight", minval=0.0, maxval=1.0)
trend_weight = input.float(0.6, "Trend Accuracy Weight", minval=0.0, maxval=1.0)

# --- Build parameter grid using np.arange ---
atr_lengths = np.arange(atr_min, atr_max + 1, atr_step, dtype=int)
multipliers = np.arange(mult_min, mult_max + mult_step * 0.5, mult_step)

n_atrs = len(atr_lengths)
n_mults = len(multipliers)
n_bars = len(close)

# --- Compute all Supertrend variants ---
# Store direction arrays for each parameter combination
all_directions = np.zeros((n_atrs, n_mults, n_bars))
all_values = np.zeros((n_atrs, n_mults, n_bars))

for i, atr_len in enumerate(atr_lengths):
    for j, mult in enumerate(multipliers):
        st_val, st_dir = ta.supertrend(high, low, close, int(atr_len), float(mult))
        all_directions[i, j, :] = np.array(st_dir)
        all_values[i, j, :] = np.array(st_val)

# --- Scoring Matrix: evaluate each parameter set ---
score_matrix = np.zeros((n_atrs, n_mults))
signal_count_matrix = np.zeros((n_atrs, n_mults))
win_rate_matrix = np.zeros((n_atrs, n_mults))

close_arr = np.array(close, dtype=np.float64)

for i in range(n_atrs):
    for j in range(n_mults):
        direction = all_directions[i, j, :]
        values = all_values[i, j, :]

        # Count signal changes in lookback window
        if n_bars > score_lookback:
            recent_dir = direction[-score_lookback:]
            signal_changes = np.sum(np.abs(np.diff(np.sign(recent_dir))) > 0)
            signal_count_matrix[i, j] = signal_changes

            # Measure trend accuracy: how often price moves in trend direction
            recent_close = close_arr[-score_lookback:]
            price_changes = np.diff(recent_close)
            trend_signs = np.sign(recent_dir[:-1])
            correct = np.sum(np.sign(price_changes) == trend_signs)
            win_rate_matrix[i, j] = correct / max(len(price_changes), 1)

            # Penalize excessive whipsaws (too many signal changes = noise)
            max_changes = score_lookback * 0.5
            whipsaw_penalty = np.clip(signal_changes / max_changes, 0, 1)

            # Combined score: high accuracy, low whipsaw
            score_matrix[i, j] = (
                trend_weight * win_rate_matrix[i, j] -
                signal_weight * whipsaw_penalty
            )

# --- Find optimal parameters using np.argmax ---
optimal_flat_idx = np.argmax(score_matrix)
opt_i, opt_j = np.unravel_index(optimal_flat_idx, score_matrix.shape)
optimal_atr = int(atr_lengths[opt_i])
optimal_mult = float(multipliers[opt_j])

# --- Consensus direction across all parameter sets ---
consensus_raw = np.mean(np.sign(all_directions), axis=(0, 1))  # average sign across grid
consensus_direction = np.sign(consensus_raw)
consensus_strength = np.abs(consensus_raw)  # 0=split, 1=unanimous

# --- Correlation matrix between supertrend signals ---
# Flatten parameter combos, compute pairwise correlation on directions
n_combos = n_atrs * n_mults
flat_dirs = all_directions.reshape(n_combos, n_bars)
if n_bars > 20 and n_combos > 1:
    # Subsample for performance: use last score_lookback bars
    sample = flat_dirs[:, -min(score_lookback, n_bars):]
    corr_matrix = np.corrcoef(sample)
    avg_correlation = np.nanmean(corr_matrix[np.triu_indices(n_combos, k=1)])

    # Per-combo average correlation (how much each agrees with others)
    combo_agreement = np.nanmean(corr_matrix, axis=1)

    # Divergence score: low correlation = parameters disagree = uncertain market
    divergence = 1.0 - np.clip(avg_correlation, 0, 1)
else:
    divergence = 0.0
    combo_agreement = np.ones(n_combos)

# --- Heatmap-style scoring: normalize to 0-100 ---
score_min = np.min(score_matrix)
score_range = np.max(score_matrix) - score_min
if score_range > 0:
    heatmap = ((score_matrix - score_min) / score_range) * 100
else:
    heatmap = np.full_like(score_matrix, 50.0)

# Row/column marginals for parameter sensitivity
atr_sensitivity = np.std(heatmap, axis=1)   # how much score varies across multipliers
mult_sensitivity = np.std(heatmap, axis=0)   # how much score varies across ATR lengths

# --- Build per-bar output series ---
# Optimal supertrend line
opt_st_val = all_values[opt_i, opt_j, :]
opt_st_dir = all_directions[opt_i, opt_j, :]

# Score time series: rolling optimal score
rolling_score = np.full(n_bars, np.nan)
for t in range(score_lookback, n_bars):
    window_dirs = all_directions[:, :, t - score_lookback:t]
    window_close = close_arr[t - score_lookback:t]
    price_chg = np.diff(window_close)
    best_score = -999
    for ii in range(n_atrs):
        for jj in range(n_mults):
            d = window_dirs[ii, jj, :-1]
            correct = np.sum(np.sign(price_chg) == np.sign(d))
            changes = np.sum(np.abs(np.diff(np.sign(d))) > 0)
            sc = trend_weight * (correct / len(price_chg)) - signal_weight * (changes / (len(d) * 0.5))
            if sc > best_score:
                best_score = sc
    rolling_score[t] = best_score * 100

# --- Plotting ---
if show_optimal:
    plot(opt_st_val, title="Optimal Supertrend", color="#FF5722")

if show_consensus:
    plot(consensus_strength * 100, title="Consensus Strength %", color="#2196F3")
    plot(consensus_direction * 50, title="Consensus Direction", color="#4CAF50")

plot(rolling_score, title="Rolling Optimal Score", color="#9C27B0")
plot(np.full(n_bars, heatmap[opt_i, opt_j]), title="Current Heatmap Score", color="#FF9800")

# Divergence as background
divergence_series = np.full(n_bars, divergence * 100)
plot(divergence_series, title="Parameter Divergence %", color="#F44336")

hline(50, title="Neutral Score", color="gray")
hline(75, title="Strong Score", color="green")
hline(25, title="Weak Score", color="red")

# Highlight when consensus is strong (>80% agreement)
bgcolor(consensus_strength > 0.8, color="rgba(76,175,80,0.08)")
# Highlight when consensus is weak (<40% agreement)
bgcolor(consensus_strength < 0.4, color="rgba(244,67,54,0.08)")

# Arrow on optimal supertrend direction changes
opt_change = np.diff(np.sign(opt_st_dir), prepend=0)
plotarrow(opt_change, title="Optimal Signal Change", colorup="#4CAF50", colordown="#F44336")
