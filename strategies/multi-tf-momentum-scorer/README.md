# Multi-TF Momentum Scorer

A multi-resolution momentum strategy that synthesizes multiple timeframes from a single data feed. Instead of requiring separate data subscriptions for each timeframe, it resamples price at geometrically-spaced intervals, computes independent momentum scores (RSI, rate of change, trend alignment) at each resolution, then combines them into a weighted composite signal. Trades are entered only when a configurable percentage of timeframes reach consensus on direction, with optional confidence-weighted position sizing.

## Conceptual Diagram

```
TF1 (5-bar):   +-+-+-+-+  Fast momentum  --\
TF2 (10-bar):  +--+--+--+ Medium momentum --\
TF3 (20-bar):  +----+----  Slow momentum  ---+-> Weighted
TF4 (40-bar):  +--------+  Trend momentum --/    Composite
TF5 (80-bar):  +--------   Macro momentum -/     Score

Each TF scored:  RSI (35%) + ROC (35%) + Trend (30%)
                            |
                 Consensus: 4/5 agree? (80%)
                            |
              YES: Enter trade, size by confidence
              NO:  Stay flat or hold existing
```

## How It Works

The strategy creates synthetic timeframes by resampling the close price at geometrically increasing intervals. Starting from a base period (default 5 bars), each subsequent timeframe multiplies the period by a configurable factor (default 2x), producing lookbacks like 5, 10, 20, 40, 80. Each resampled series is interpolated back to bar-level resolution for scoring.

At each timeframe resolution, three independent momentum metrics are computed. RSI captures mean-reversion momentum, mapped from its 0-100 range to a normalized -1 to +1 score. Rate of change measures raw price momentum as a percentage, clipped and normalized. Trend alignment uses linear regression slope over the timeframe window, normalized by price level to produce a directional score.

The three scores are combined per timeframe using fixed weights (35% RSI, 35% ROC, 30% trend), then aggregated across all timeframes using logarithmic weighting that gives higher timeframes more influence. The consensus metric measures what fraction of timeframes agree on direction. Trades trigger only when the composite score exceeds a threshold and consensus reaches the configured level.

Position sizing optionally scales with confidence, defined as the product of composite score magnitude and consensus percentage. This means high-conviction signals with broad timeframe agreement receive larger allocations, while marginal signals get minimal exposure.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Base Period | 5 | 2-20 | Shortest synthetic timeframe lookback in bars |
| Number of Timeframes | 5 | 2-8 | How many synthetic timeframes to generate |
| Timeframe Multiplier | 2.0 | 1.5-4.0 | Geometric scaling factor between timeframes |
| Consensus Threshold | 0.7 | 0.3-1.0 | Fraction of timeframes that must agree for entry |
| RSI Length | 14 | 5-30 | RSI calculation period |
| ROC Length | 10 | 3-30 | Rate of change calculation period |
| Confidence-Weighted Sizing | true | - | Scale position size by signal confidence |
| Max Risk % | 2.0 | 0.5-5.0 | Maximum position size as percentage |

## Python Advantage

The multi-resolution resampling, per-timeframe scoring, and matrix-based consensus calculation require dynamic array generation and weighted aggregation impossible in Pine Script:

```python
# Generate synthetic timeframes with geometric spacing
tf_periods = [int(base_period * (tf_multiplier ** i)) for i in range(num_tf)]

# Resample and score each timeframe independently
tf_scores = np.zeros((num_tf, n))
for idx, period in enumerate(tf_periods):
    resampled = np.interp(np.arange(n), np.arange(0, n, period), close[::period])
    rsi_score = (calc_rsi(resampled, rsi_len) - 50) / 50
    roc_score = np.clip(calc_roc(resampled, period) / 5, -1, 1)
    trend = calc_trend_score(resampled, min(period, 30))
    tf_scores[idx] = np.average([rsi_score, roc_score, trend], axis=0, weights=[.35,.35,.30])

# Matrix consensus: count agreeing timeframes across all bars at once
directions = np.sign(tf_scores)  # shape: (num_tf, n)
consensus = np.sum(directions > 0, axis=0) / num_tf  # vectorized across bars

# Log-weighted aggregation
tf_weights = np.log(np.array(tf_periods) + 1)
composite = np.sum(tf_weights[:, None] * tf_scores, axis=0) / np.sum(tf_weights)
```

Pine Script cannot create arrays of arrays, dynamically resample data, perform matrix operations across multiple synthetic timeframes, or use np.average with computed weights. This entire multi-resolution analysis framework is exclusive to Python.

## When to Use

Effective on 15-minute to daily charts for swing and position trading. Works best on trending instruments like index ETFs, major forex pairs, and liquid futures where momentum signals at multiple scales tend to align during strong moves. Use higher consensus thresholds (0.8-1.0) for conservative entries, lower thresholds (0.5-0.6) for more frequent trades. Increase the number of timeframes for broader market analysis on daily charts. Reduce the base period for intraday scalping.

## Risk Management

Multi-timeframe consensus inherently lags because higher timeframes respond slowly to reversals. Exit signals may arrive late during sharp reversals, so always use hard stop-losses independent of the strategy signals. The confidence-weighted sizing helps limit exposure on weak signals but does not replace proper risk management. Avoid using this strategy in ranging markets with no clear directional bias, where timeframes will produce conflicting signals and low consensus. Start with default parameters and paper trade before adjusting.

## Combining with Other Indicators

- Use with ATR-based trailing stops to lock in profits during extended trends, since the strategy is better at entries than exits during reversals
- Combine with volume confirmation (OBV or CMF) to filter out momentum signals that lack participation
- Pair with support/resistance or Fibonacci levels to time entries within the consensus direction, improving entry prices
