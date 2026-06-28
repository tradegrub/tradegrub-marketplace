# Neural Weight Oscillator

A self-adapting composite oscillator that fuses three distinct market behavior models -- Trend, Mean Reversion, and Momentum -- into a single normalized reading. Rather than using fixed blending ratios, the indicator applies an analytic hierarchy pairwise comparison method to determine which behavioral model best explains current price action. The resulting weights shift in real time, so the oscillator automatically emphasizes trend-following signals in trending markets, mean-reversion signals in range-bound conditions, and momentum signals during breakout phases.

## Conceptual Diagram

```
  ADX/DMI ────> Trend Score ──────┐
                                  │   Pairwise Comparison
  Z-Score/BB ──> Revert Score ────┼──> Matrix (3x3) ──> Eigenvector
                                  │   Weights
  ROC/RSI' ───> Momentum Score ───┘       │
                                          v
                    ┌─────────────────────────────┐
                    │  W_t * Trend + W_r * Revert │
                    │  + W_m * Momentum           │
                    └──────────┬──────────────────┘
                               v
              ┌──────────────────────────────┐
              │   Oscillator (0-100 scale)   │
              │  70 ---- Overbought -------- │
              │  50 ---- Neutral ----------- │
              │  30 ---- Oversold ---------- │
              └──────────────────────────────┘
                     Regime Colors:
               Blue=Trend  Orange=Revert  Purple=Momentum
```

## How It Works

The oscillator begins by computing three independent factor scores. The Trend Score uses the Directional Movement Index (ADX with plus/minus DI) to measure trend strength and direction. A strong uptrend yields a score near +1, a strong downtrend near -1, and a trendless market near 0.

The Mean Reversion Score combines z-score analysis with Bollinger Band positioning. The z-score measures how far price has deviated from its rolling mean in standard deviation units, while the BB position captures where price sits within the volatility envelope. These are blended and inverted so that extreme overextension produces a signal to revert toward the mean.

The Momentum Score merges Rate of Change with the first derivative of RSI. ROC captures raw price velocity, while the RSI derivative detects acceleration and deceleration in momentum. Both are normalized by their rolling standard deviations to maintain consistent sensitivity across different volatility regimes.

To determine dynamic weights, the indicator builds a pairwise comparison matrix from observed market conditions. ADX strength, absolute z-score magnitude, and ROC variance each represent how well that factor model explains recent price behavior. The geometric mean method (an approximation of the principal eigenvector from Analytic Hierarchy Process theory) converts these pairwise ratios into normalized weights that sum to 1.0. When trending conditions dominate, the trend weight rises toward 0.6-0.8; in mean-reverting ranges, the reversion weight takes over.

The final composite score is the weighted sum of all three factor scores, rescaled to a 0-100 range. Readings above 70 indicate overbought conditions within the dominant regime, readings below 30 indicate oversold conditions, and the weight percentages plotted alongside reveal exactly which behavioral model is driving the signal.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Trend Period | 14 | 5-50 | Lookback for ADX/DMI trend detection |
| Mean Reversion Period | 20 | 5-50 | Lookback for z-score and Bollinger Bands |
| Momentum Period | 10 | 3-30 | Lookback for ROC and RSI derivative |
| Regime Detection Window | 50 | 20-100 | Rolling window for regime strength estimation |
| Overbought Level | 70 | 60-90 | Upper threshold for overbought signals |
| Oversold Level | 30 | 10-40 | Lower threshold for oversold signals |

## Python Advantage

The core of this indicator is a multi-criteria decision analysis that requires matrix algebra -- something impossible in Pine Script:

```python
# Build pairwise strength ratios and extract weights via geometric mean
raw_strengths = np.column_stack([adx_strength, zscore_strength, mom_strength])

weights = np.zeros((n_bars, 3))
for i in range(3):
    ratios = raw_strengths[:, i:i+1] / (raw_strengths + 1e-10)
    geo_mean = np.prod(ratios, axis=1) ** (1.0 / 3.0)
    weights[:, i] = geo_mean

# Normalize so weights sum to 1.0 at each bar
weight_sums = np.sum(weights, axis=1, keepdims=True)
weights = weights / (weight_sums + 1e-10)

# Weighted composite using vectorized operations across all bars
composite = w_trend * trend_score + w_revert * revert_score + w_mom * mom_score
```

The np.column_stack, np.prod with axis reduction, and matrix broadcasting allow the entire pairwise comparison to run vectorized across all bars simultaneously. Pine Script has no matrix type, no eigenvector extraction, and no way to dynamically compute weights from multi-factor pairwise ratios.

## When to Use

The Neural Weight Oscillator works across all timeframes and asset classes. It is particularly effective when you are unsure whether the market is trending, ranging, or in a momentum breakout, because the weight distribution tells you directly. Use on daily charts for swing trading signals, or on 1-hour and 4-hour charts for active trading. The regime weights panel is valuable on its own as a market state classifier even without trading the oscillator signals.

## Risk Management

Overbought/oversold readings are regime-relative, not absolute. A reading of 75 during a strong trend (high trend weight) is less likely to reverse than 75 during a mean-reversion regime. Always confirm signals with price action and volume. Use stop-losses at recent swing points. Position size inversely to the regime detection window volatility reading. Avoid trading oscillator extremes during low-confidence periods when all three weights are near 0.33 (no clear regime).

## Combining with Other Indicators

- Pair with volume-based indicators (OBV, CMF) to confirm that regime shifts have volume support
- Use alongside the ATR Percent indicator for volatility-adjusted position sizing during regime transitions
- Combine with the Chart Pattern Scanner to validate that oscillator signals align with structural pattern breakouts
