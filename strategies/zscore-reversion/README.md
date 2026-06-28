# Z-Score Mean Reversion

The Z-Score Mean Reversion strategy applies classical statistical normalization to price data, measuring how many standard deviations the current price sits from its moving average. The Z-score is a foundational concept in statistics that transforms any distribution into a standardized scale, making it possible to identify extreme readings regardless of the instrument's price level or volatility. When the Z-score reaches extreme thresholds, the strategy bets on a return to the mean.

## Conceptual Diagram

```
Z-Score
 |
 +2 ┄┄┄┄┄┄┄┄┄┄╱╲┄┄┄┄┄┄┄┄┄┄┄┄ Entry Threshold
 |           ╱    ╲
 |    /\   ╱        ╲
 |   /  \ ╱          ╲    /\
  0 ─/────X────────────╲──/──╲── Exit Level (mean)
 |  /                    ╲/    ╲
 |                              ╲
 -2 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╲ Entry Threshold
 |                                ╲╱
 +──────────────────────────────────── Time
           🔴 SHORT         exit    🟢 LONG
       (z crosses           (z crosses
        below +2)            above -2)
        exit at 0            exit at 0
```

## How It Works

The strategy computes a simple moving average and standard deviation of closing prices over a configurable lookback period. The Z-score is then calculated as `(close - sma) / stdev`, normalizing price into units of standard deviations from the mean. A Z-score of -2 means the current price is two standard deviations below its recent average; a Z-score of +2 means it is two standard deviations above.

Long entries trigger when the Z-score crosses above the negative entry threshold (e.g., -2.0). The crossover is important: it means the Z-score was below -2 and has begun recovering, timing the entry at the start of the reversion move rather than during the initial drop. Short entries trigger when the Z-score crosses below the positive entry threshold.

Exits occur when the Z-score returns to the exit level (default 0.0, the mean). For longs, this means the Z-score has recovered from its negative extreme back to the average. For shorts, the Z-score has dropped from its positive extreme back to neutral. This captures the full reversion move from extreme to mean.

The strategy is bidirectional, trading both oversold bounces (long) and overbought reversals (short). The Z-score normalization makes thresholds portable across instruments: a Z-score of 2.0 represents the same statistical extremity whether applied to a $5 stock or a $5,000 index.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback Length | 20 | 5 - 200 | Period for calculating the moving average and standard deviation |
| Entry Z-Score | 2.0 | 1.0 - 4.0 | Z-score threshold for triggering entry signals |
| Exit Z-Score | 0.0 | -1.0 - 1.0 | Z-score level at which positions are closed |

## Python Advantage

The entire Z-score computation is a single vectorized expression operating on numpy arrays, with crossover detection for precise entry timing:

```python
# Vectorized Z-score computation — three array operations in one line
sma = ta.sma(close, length)
stdev = ta.stdev(close, length)
zscore = (close - sma) / stdev

# Crossover against scalar threshold — returns full boolean array
if ta.crossover(zscore, -entry_z)[-1]:
    strategy.entry("Long", strategy.LONG)

# Manual crossover via consecutive bar comparison
if zscore[-1] > exit_z and zscore[-2] <= exit_z:
    strategy.close("Long")
```

The `(close - sma) / stdev` expression performs element-wise subtraction and division across the entire price history in a single pass. Pine Script computes this identically per bar, but Python's array arithmetic enables downstream analysis: you could compute `np.percentile(zscore, 95)` or `np.histogram(zscore)` for distribution analysis, operations that are impossible in Pine. The `ta.crossover(zscore, -entry_z)` call compares the full Z-score array against a scalar, returning every crossover point in history.

## When to Use

Z-Score Mean Reversion works best on instruments with stable, mean-reverting distributions: large-cap stocks, index ETFs, major forex pairs, and bond futures. It is especially effective on daily and 4-hour timeframes where the statistical properties of price distributions are more reliable. The strategy struggles on trending instruments in parabolic moves where Z-scores can remain extreme for extended periods. It is also well-suited for pairs trading, where the Z-score is applied to a spread rather than a single instrument.

## Risk Management

Set hard stops at a Z-score beyond the entry threshold (e.g., if entering at Z=-2, stop at Z=-3 or a fixed percentage loss). The exit at Z=0 limits holding time, but in strongly trending markets the Z-score may never return to zero, resulting in extended drawdowns. Consider a time-based exit for trades that fail to revert within a specified number of bars. Raising the entry Z-score to 2.5 or 3.0 produces fewer but higher-conviction signals at more extreme statistical levels.

## Combining with Other Indicators

- **Regression Reversion** provides a complementary percentage-deviation approach to the same mean-reversion concept.
- **RSI Mean Reversion** adds momentum oscillator confirmation to the statistical Z-score signal.
- **Std Dev Channel** offers a visual channel representation of the same standard-deviation-based extremes.
