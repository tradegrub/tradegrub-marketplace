# Price Distribution Analysis

A statistical indicator that uses matplotlib and numpy to compute rolling price distributions, showing where current price sits relative to its recent history through z-scores, percentile ranks, and probability density measurements. The indicator highlights statistically extreme price levels that often precede mean-reversion moves.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

For each bar, the indicator builds a histogram of closing prices over the lookback window using numpy histogram binning. This creates a probability distribution of where price has spent time recently. The current price is then located within this distribution to compute three metrics: z-score (standard deviations from the rolling mean), percentile rank (what percentage of recent prices are below the current level), and bin density (the probability density of the bin containing the current price).

Z-scores beyond the configurable warning threshold flag statistically unusual price levels. A z-score above +2.0 means price is more than two standard deviations above its recent mean, a condition that historically reverts. Conversely, z-scores below -2.0 signal unusually depressed prices. Percentile rank provides an intuitive 0-100 scale: values above 90 mean price is near the top of its recent range, while values below 10 indicate the bottom.

Background shading highlights overbought (red) and oversold (green) zones. Labels mark extremes with exact z-score and percentile values. A summary label on the current bar shows all three metrics for quick reference.

## Parameters

| Name | Default | Range | Description |
|------|---------|-------|-------------|
| Lookback Period | 100 | 20-500 | Number of bars for the distribution window |
| Number of Bins | 20 | 5-50 | Histogram resolution for density computation |
| Z-Score Warning Level | 2.0 | 0.5-4.0 | Threshold for overbought and oversold alerts |
| Show Labels | True | on/off | Toggle annotation labels at extreme readings |
| Show Levels | True | on/off | Toggle horizontal reference lines |

## Python Advantage

Rolling distribution analysis runs efficiently by computing histograms and statistical metrics across configurable windows:

```python
for i in range(lookback, n):
    window = close[i - lookback:i + 1]
    hist_counts, bin_edges = np.histogram(window, bins=num_bins, density=True)
    zscore[i] = (price - np.mean(window)) / np.std(window)
    percentile_rank[i] = np.sum(window <= price) / len(window) * 100
```

Numpy histogram and statistical functions handle the heavy computation within each window, making the per-bar calculation fast even on large datasets.

## When to Use

This indicator works best as a mean-reversion filter on instruments that trade in ranges or oscillate around a trend. Apply it to stocks in consolidation phases, ETFs near support or resistance zones, and forex pairs in ranging conditions. On trending instruments, use the z-score to identify extended moves that may pause or retrace. Daily and 4-hour timeframes produce cleaner distributions than sub-hourly charts where noise can distort the density profile.

## Interpretation

A z-score above +2.0 combined with a percentile rank above 95 signals a statistically extreme overbought condition. This does not guarantee a reversal but indicates price is far from its recent norm. Look for confirmation from volume decline or momentum divergence before fading the move. Conversely, deeply negative z-scores with low percentile rank highlight potential buying opportunities in oversold conditions.

Bin density adds context: if the current price sits in a high-density bin, it means price has spent significant time at this level recently and it may act as a magnet. Low-density bins indicate price is in unfamiliar territory, increasing the probability of a sharp move back toward the distribution center.

## Combining with Other Indicators

- **RSI divergence:** When the z-score flags an extreme but RSI shows divergence, the probability of a reversal increases significantly compared to either signal alone.
- **Volume profile:** Compare the distribution indicator density with actual volume-at-price data to confirm whether price levels with high density also have high traded volume, strengthening support and resistance readings.
- **Bollinger Bands:** The z-score provides a similar concept to Bollinger Band width. Use both together to confirm when price has stretched beyond normal statistical boundaries.
- **ATR trailing stop:** Use distribution extremes as entry signals and ATR-based stops for risk management, combining statistical edge with volatility-adapted exits.
