from tg_scripting import *

# --- Inputs ---
trend_len = input.int(14, "Trend Period", minval=5, maxval=50)
revert_len = input.int(20, "Mean Reversion Period", minval=5, maxval=50)
mom_len = input.int(10, "Momentum Period", minval=3, maxval=30)
regime_len = input.int(50, "Regime Detection Window", minval=20, maxval=100)
overbought = input.float(70.0, "Overbought Level", minval=60.0, maxval=90.0)
oversold = input.float(30.0, "Oversold Level", minval=10.0, maxval=40.0)

# --- Factor 1: Trend Strength (ADX-based) ---
plus_di, minus_di, adx = ta.dmi(high, low, close, trend_len)
trend_direction = np.where(plus_di > minus_di, 1.0, -1.0)
trend_score_raw = adx / 100.0 * trend_direction
trend_score = np.clip(trend_score_raw, -1.0, 1.0)

# --- Factor 2: Mean Reversion (Z-score + Bollinger position) ---
bb_upper, bb_basis, bb_lower = ta.bb(close, revert_len, 2.0)
bb_width = bb_upper - bb_lower
bb_position = np.where(bb_width != 0, (close - bb_lower) / bb_width, 0.5)

rolling_mean = ta.sma(close, revert_len)
rolling_std = ta.stdev(close, revert_len)
z_score = np.where(rolling_std != 0, (close - rolling_mean) / rolling_std, 0.0)
z_norm = np.clip(z_score / 3.0, -1.0, 1.0)

revert_score = -(z_norm * 0.6 + (bb_position * 2.0 - 1.0) * 0.4)
revert_score = np.clip(revert_score, -1.0, 1.0)

# --- Factor 3: Momentum (ROC + RSI derivative) ---
roc_val = ta.roc(close, mom_len)
roc_norm = np.clip(roc_val / np.where(ta.stdev(roc_val, regime_len) != 0,
                                       ta.stdev(roc_val, regime_len) * 3.0, 1.0), -1.0, 1.0)

rsi_val = ta.rsi(close, mom_len)
rsi_change = ta.change(rsi_val, 3)
rsi_deriv_norm = np.clip(rsi_change / 30.0, -1.0, 1.0)

mom_score = roc_norm * 0.5 + rsi_deriv_norm * 0.5
mom_score = np.clip(mom_score, -1.0, 1.0)

# --- Regime Detection via rolling statistics ---
volatility = ta.stdev(close, regime_len) / ta.sma(close, regime_len)
trend_persistence = ta.sma(np.abs(ta.change(close, 1)), regime_len)
mean_rev_potential = ta.sma(np.abs(z_score), regime_len)

# --- Best-Worst Method / Analytic Hierarchy pairwise weights ---
# Build pairwise preference intensities from market conditions
# Higher ADX => trend dominates; High |z-score| => mean reversion; High ROC variance => momentum
adx_strength = np.clip(adx / 50.0, 0.1, 1.0)
zscore_strength = np.clip(np.abs(ta.sma(z_score, 5)) / 2.0, 0.1, 1.0)
mom_strength = np.clip(np.abs(ta.sma(roc_val, 5)) / (ta.stdev(roc_val, regime_len) + 1e-10), 0.1, 1.0)

# Construct pairwise comparison matrix row by row using np.outer scaling
# For each bar, build a 3x3 matrix and extract principal eigenvector weights
raw_strengths = np.column_stack([adx_strength, zscore_strength, mom_strength])

# Vectorized weight calculation via normalization of strength ratios
# Approximation of eigenvector method: geometric mean of each row in pairwise matrix
n_bars = len(close)
weights = np.zeros((n_bars, 3))
for i in range(3):
    # Pairwise ratio: strength_i / strength_j for all j
    ratios = raw_strengths[:, i:i+1] / (raw_strengths + 1e-10)
    # Geometric mean across columns = product^(1/3)
    geo_mean = np.prod(ratios, axis=1) ** (1.0 / 3.0)
    weights[:, i] = geo_mean

# Normalize weights to sum to 1
weight_sums = np.sum(weights, axis=1, keepdims=True)
weights = weights / (weight_sums + 1e-10)

w_trend = weights[:, 0]
w_revert = weights[:, 1]
w_mom = weights[:, 2]

# --- Composite Oscillator ---
composite_raw = w_trend * trend_score + w_revert * revert_score + w_mom * mom_score

# Scale to 0-100 range
oscillator = (composite_raw + 1.0) / 2.0 * 100.0
oscillator = np.clip(oscillator, 0.0, 100.0)
oscillator_smooth = ta.ema(oscillator, 3)

# --- Dominant regime label via argmax ---
regime_labels = np.argmax(weights, axis=1)  # 0=trend, 1=revert, 2=momentum

# Color by regime
regime_colors = np.where(regime_labels == 0, "#2196F3",
                 np.where(regime_labels == 1, "#FF9800", "#9C27B0"))

# --- Plots ---
osc_plot = plot(oscillator_smooth, title="NW Oscillator", color="#26A69A")
mid_plot = plot(np.full_like(close, 50.0), title="Midline", color="#78909C")
fill(osc_plot, mid_plot, color=np.where(oscillator_smooth > 50, "rgba(38,166,154,0.15)", "rgba(239,83,80,0.15)"))

hline(overbought, title="Overbought", color="#EF5350")
hline(oversold, title="Oversold", color="#26A69A")
hline(50.0, title="Neutral", color="#78909C")

plot(w_trend * 100, title="Trend Weight %", color="#2196F3")
plot(w_revert * 100, title="Reversion Weight %", color="#FF9800")
plot(w_mom * 100, title="Momentum Weight %", color="#9C27B0")

# Signal markers
bull_signal = ta.crossover(oscillator_smooth, oversold)
bear_signal = ta.crossunder(oscillator_smooth, overbought)
plotshape(bull_signal, title="Bull Signal", style="triangleup", location="belowbar", color="#26A69A")
plotshape(bear_signal, title="Bear Signal", style="triangledown", location="abovebar", color="#EF5350")
