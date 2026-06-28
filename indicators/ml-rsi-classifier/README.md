# ML RSI Classifier

The ML RSI Classifier transforms the traditional Relative Strength Index into a multi-dimensional feature space and applies weighted k-nearest-neighbor classification to identify the current market regime. Rather than relying on fixed overbought/oversold thresholds, the indicator extracts five behavioral features from RSI -- momentum, acceleration, regime z-score, price-RSI divergence strength, and volatility-adjusted level -- then searches historical analogs to classify the market as trending-up, trending-down, ranging, or reversal-imminent. Each classification carries a confidence score derived from the vote distribution of nearest neighbors, filtering out low-conviction signals.

## Conceptual Diagram

```
  RSI Feature Space             KNN Classification
  ─────────────────            ─────────────────────
  ┌─────────────┐    extract    ┌──────────────────┐
  │   Raw RSI   │───────────>  │ Feature Vector    │
  │   (14-bar)  │              │ [mom, accel, z,   │
  └─────────────┘              │  div, vol_adj]    │
                               └────────┬─────────┘
  ┌─────────────┐                       │ distance
  │  ATR / Vol  │───> vol_adj           v
  └─────────────┘              ┌──────────────────┐
  ┌─────────────┐              │  K=8 Nearest     │
  │  Price corr │───> div      │  Analog Vectors  │
  └─────────────┘              │  (weighted vote)  │
                               └────────┬─────────┘
                                        v
                    ┌──────────────────────────────┐
                    │  UP  │ DOWN │ RANGE │REVERSAL│
                    │  65% │  12% │  15%  │   8%   │
                    └──────────────────────────────┘
                         Winner: UP (conf 65%)
                              ▲ signal
```

## How It Works

The indicator begins by computing a standard RSI, then derives five features at each bar. RSI momentum is the first difference of RSI values, capturing the rate of change. RSI acceleration is the second difference, revealing whether momentum itself is speeding up or slowing down. A rolling z-score normalizes RSI relative to its own recent distribution, identifying when RSI is unusually high or low for the current regime rather than using fixed 70/30 thresholds.

The fourth feature measures price-RSI divergence strength using a rolling Pearson correlation (np.corrcoef) between price and RSI over the feature window. A correlation near +1 means price and RSI move together (no divergence), while values near -1 signal strong bearish or bullish divergence. The fifth feature is a volatility-adjusted RSI that scales the raw RSI reading by the ATR z-score, giving more weight to RSI signals that occur during unusual volatility conditions.

These five features form a vector for each bar. The indicator stores vectors from the past N bars (the analog lookback) as historical reference points. Each historical vector is labeled based on what the market actually did next: forward returns above +0.5% are labeled trending-up, below -0.5% trending-down, and anything in between is ranging. A special reversal-imminent label is applied when RSI was at an extreme (above 70 or below 30) and the subsequent move opposed the extreme.

For the current bar, the indicator computes Euclidean distances (np.linalg.norm) to all stored historical vectors, selects the k nearest neighbors (np.argsort), and performs inverse-distance-weighted voting across the four classes. The class with the highest weighted vote total wins, and its vote proportion becomes the confidence score. Only classifications exceeding the confidence threshold produce visual signals on the chart.

The output displays the RSI line, a confidence percentage line, and shape markers for trend-up (green triangles), trend-down (red triangles), and reversal alerts (orange diamonds). Background coloring provides additional context for the active regime classification.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| RSI Length | 14 | 5 - 50 | Lookback period for RSI calculation |
| K Neighbors | 8 | 3 - 25 | Number of nearest neighbors for KNN voting |
| Analog Lookback | 200 | 50 - 500 | How many historical bars to search for analogs |
| Feature Window | 5 | 3 - 20 | Window size for feature extraction (correlation, z-score) |
| Confidence Threshold | 0.60 | 0.30 - 0.95 | Minimum vote proportion to display a classification signal |
| Show Classification Signals | true | -- | Toggle shape markers on the chart |

## Python Advantage

The entire KNN classification pipeline -- feature engineering, vectorized distance calculations, and weighted voting -- runs in pure numpy and would be impossible in Pine Script:

```python
# Build 5-dimensional feature vectors per bar
features = np.column_stack([
    np.diff(rsi_arr, prepend=rsi_arr[0]),           # momentum
    np.diff(rsi_momentum, prepend=rsi_momentum[0]), # acceleration
    rolling_zscore(rsi_arr, window),                 # regime z-score
    np.corrcoef(price_seg, rsi_seg)[0, 1],          # divergence
    rsi_arr * (1 + 0.2 * atr_zscore),               # vol-adjusted
])

# Vectorized KNN: distance to all analogs in one call
diffs = history_features - current_vec
distances = np.linalg.norm(diffs, axis=1)
nearest_idx = np.argsort(distances)[:k_neighbors]

# Inverse-distance weighted voting
weights = 1.0 / (distances[nearest_idx] + 1e-10)
vote_counts = np.array([np.sum(weights[labels == c]) for c in range(4)])
confidence = np.max(vote_counts) / np.sum(vote_counts)
```

Pine Script has no matrix operations, no distance calculations across feature vectors, no argsort, and no way to store and query multi-dimensional analog databases. This indicator requires numpy's linear algebra and array manipulation at every step.

## When to Use

The ML RSI Classifier works best on liquid instruments with sufficient history to populate the analog database. Use it on daily and 4-hour timeframes for swing trading, or on 15-minute to 1-hour charts for intraday classification. It excels in markets that cycle between trending and ranging regimes, such as major forex pairs, large-cap equities, and index futures. The reversal-imminent classification is particularly valuable near earnings, FOMC announcements, or other catalysts where RSI extremes tend to resolve rapidly.

## Risk Management

Never trade classification signals alone. The confidence score is a statistical measure of analog similarity, not a guarantee of future returns. Use a stop-loss placed beyond the recent swing high/low when acting on trend or reversal signals. Position size inversely to the ATR to keep dollar risk consistent. Be cautious with the reversal-imminent signal during strong trends -- reversals in a momentum regime often fail. Reduce K neighbors on lower timeframes where market microstructure changes faster than analog patterns persist.

## Combining with Other Indicators

- Pair with a volume-based indicator (OBV, CMF) to confirm that classified trend directions have volume support behind them.
- Use alongside Bollinger Bands or Keltner Channels to validate reversal-imminent signals that occur at band extremes.
- Combine with a trend filter like ADX: only act on trend-up/down classifications when ADX confirms a trending regime (above 25).
