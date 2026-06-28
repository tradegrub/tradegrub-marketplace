# Supertrend Sensitivity Matrix

A parameter optimization engine that runs multiple Supertrend calculations simultaneously across a configurable grid of ATR lengths and multipliers. It evaluates each combination using trend accuracy and whipsaw metrics, finds optimal parameters for current market conditions, measures consensus across all variants, and quantifies parameter divergence through correlation analysis. The result is a real-time sensitivity map that adapts to changing volatility regimes.

## Conceptual Diagram

```
  Parameter Grid (np.arange)
  ATR:  [5, 10, 15, 20, 25]
  Mult: [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

  For each (ATR, Mult) pair:
  +---------------------------+
  | ta.supertrend(H,L,C,A,M)  |
  | --> direction[], value[]  |
  +-------------+-------------+
                |
    +-----------+-----------+
    |                       |
    v                       v
  [Accuracy Score]    [Whipsaw Count]
  correct/total       signal_changes
    |                       |
    v                       v
  score = w1*accuracy - w2*whipsaw_penalty

  All scores --> Score Matrix [n_atrs x n_mults]
       |
       +---> np.argmax --> Optimal (ATR, Mult)
       +---> np.corrcoef --> Divergence Score
       +---> np.mean(sign) --> Consensus Direction
       +---> np.std(rows/cols) --> Sensitivity Analysis
```

## How It Works

The indicator builds a parameter grid using np.arange for both ATR lengths and multipliers, then computes Supertrend values and directions for every combination. With default settings, this creates a 5x7 matrix of 35 simultaneous Supertrend calculations, each producing full-length direction and value arrays stored in 3D numpy arrays.

Each parameter combination is scored over a configurable lookback window using two metrics. Trend accuracy measures how often price moves in the direction indicated by the Supertrend. Whipsaw penalty counts direction changes and normalizes against a maximum threshold. The final score blends these with configurable weights, rewarding parameter sets that catch trends accurately while avoiding excessive signal noise.

The optimal parameter set is found using np.argmax on the flattened score matrix, then unraveled back to grid coordinates with np.unravel_index. This optimal Supertrend line is plotted as the primary signal. A rolling version recomputes the optimal score at each bar, showing how the best achievable performance evolves over time.

Consensus analysis averages the sign of all direction arrays across the entire parameter grid. When consensus strength is high (above 80%), most parameter combinations agree on trend direction, indicating a robust trend. When consensus is low (below 40%), parameters disagree, suggesting choppy or transitional conditions. Correlation analysis using np.corrcoef on recent direction windows measures how similarly different parameter sets behave, with low correlation indicating high parameter sensitivity.

Sensitivity is measured through row and column standard deviations of the normalized heatmap. High ATR sensitivity means small changes in ATR length produce large score differences. High multiplier sensitivity means the indicator is fragile to multiplier choice. Traders should prefer parameter regions where sensitivity is low, indicating robust performance.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Min ATR Length | 5 | 2-50 | Smallest ATR period in the search grid |
| Max ATR Length | 25 | 5-100 | Largest ATR period in the search grid |
| ATR Length Step | 5 | 1-10 | Step size between ATR periods |
| Min Multiplier | 1.0 | 0.5-5.0 | Smallest multiplier in the search grid |
| Max Multiplier | 4.0 | 1.0-10.0 | Largest multiplier in the search grid |
| Multiplier Step | 0.5 | 0.1-2.0 | Step size between multipliers |
| Scoring Lookback | 50 | 10-200 | Bars used for scoring each parameter set |
| Show Optimal Supertrend | true | - | Display the optimal Supertrend line |
| Show Consensus Direction | true | - | Display consensus strength and direction |
| Signal Change Weight | 0.4 | 0.0-1.0 | Weight of whipsaw penalty in scoring |
| Trend Accuracy Weight | 0.6 | 0.0-1.0 | Weight of directional accuracy in scoring |

## Python Advantage

```python
# 3D array stores all Supertrend variants: [atr_idx, mult_idx, bar]
all_directions = np.zeros((n_atrs, n_mults, n_bars))
for i, atr_len in enumerate(atr_lengths):
    for j, mult in enumerate(multipliers):
        _, st_dir = ta.supertrend(high, low, close, int(atr_len), float(mult))
        all_directions[i, j, :] = np.array(st_dir)

# Consensus via mean of signs across entire parameter grid
consensus_raw = np.mean(np.sign(all_directions), axis=(0, 1))

# Correlation matrix across all parameter combinations
flat_dirs = all_directions.reshape(n_combos, n_bars)
corr_matrix = np.corrcoef(flat_dirs[:, -lookback:])
divergence = 1.0 - np.nanmean(corr_matrix[np.triu_indices(n_combos, k=1)])

# Optimal parameter detection via argmax + unravel
optimal_flat_idx = np.argmax(score_matrix)
opt_i, opt_j = np.unravel_index(optimal_flat_idx, score_matrix.shape)
```

This grid search over 35+ Supertrend variants with correlation analysis, 3D array operations, and automatic parameter optimization requires numpy array broadcasting and matrix operations that are impossible in traditional scripting languages.

## When to Use

Ideal for any trending instrument where Supertrend is used as a primary or confirmation signal. Most valuable during volatility regime transitions when previously optimal parameters may degrade. Use on 15-minute to daily timeframes. Particularly effective on instruments with variable volatility like crypto, commodity futures, and growth stocks. Run the matrix analysis periodically to validate that your chosen Supertrend parameters remain near-optimal.

## Risk Management

The optimal parameters are backward-looking and will lag during sudden regime changes. When consensus strength drops below 40%, reduce position size or step aside. High parameter divergence (above 60%) indicates the market is not well-suited for trend-following with Supertrend. Do not over-fit by using very short scoring lookbacks (below 20 bars), as this produces unstable optimal parameters. The rolling score naturally declines during ranging markets, providing a built-in regime filter.

## Combining with Other Indicators

- Use with ADX to confirm trend strength before trusting the optimal Supertrend signal
- Pair with Session Edge Profiler to apply session-specific Supertrend parameters
- Combine with Squeeze Momentum to enter only when the optimal Supertrend aligns with a squeeze breakout direction
