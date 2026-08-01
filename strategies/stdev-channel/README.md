# Std Dev Channel Reversion

The Standard Deviation Channel Reversion strategy builds a price channel around a linear regression line, using standard deviation bands as dynamic overbought/oversold extremes. Unlike Bollinger Bands, which center on a simple moving average, this channel follows the trend slope, providing a more accurate "fair value" corridor. The strategy trades mean reversion from the channel edges back to the regression center.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The strategy calculates a linear regression line using `ta.linreg(close, length)` as the channel center. This line represents the statistically best-fit trend through recent prices, capturing both direction and slope. Standard deviation of closing prices over the same period defines the channel width, multiplied by a configurable factor (default 2.0).

Long entries trigger when price crosses back above the lower channel boundary. This crossover indicates price has been statistically extended to the downside and is beginning to recover toward the regression mean. Short entries fire when price crosses below the upper channel boundary, signaling an overextended rally starting to fade.

Both directions exit at the regression line itself. This is the key insight: the strategy does not try to ride moves beyond fair value. It captures the reversion from one extreme back to the center, which is the highest-probability portion of the move.

The channel automatically adapts to both trend direction (via regression slope) and volatility (via standard deviation width), making it more responsive than static support/resistance levels.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Channel Length | 50 | 10 - 200 | Lookback period for regression and standard deviation |
| Std Dev Multiplier | 2.0 | 0.5 - 4.0 | Number of standard deviations for channel width |

## Python Advantage

The channel construction combines linear regression and standard deviation into a clean vectorized pipeline:

```python
# Linear regression as channel center — full-array computation
basis = ta.linreg(close, length)
stdev = ta.stdev(close, length)

# Channel boundaries via vectorized array arithmetic
upper = basis + stdev * mult
lower = basis - stdev * mult

# Crossover detection on dynamically computed channel arrays
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)
```

The `basis + stdev * mult` expression performs element-wise addition and multiplication across entire numpy arrays in a single operation. Pine would compute this identically per-bar, but Python's array arithmetic makes the intent clearer and enables downstream array operations like percentile analysis or conditional masking.

## When to Use

Standard deviation channels work best on instruments with established trends where temporary deviations from the regression line are common: large-cap equities, index ETFs, and major forex pairs. Daily and 4-hour timeframes produce the cleanest signals. The strategy struggles in trendless, choppy markets where the regression line has no meaningful slope.

## Risk Management

Place hard stops one standard deviation beyond the channel boundary (e.g., at `lower - stdev * 0.5` for longs). The regression line exit limits profit per trade but also limits time in the market, reducing exposure. In strongly trending markets, the lower channel may keep rising, causing repeated re-entries; consider a maximum position frequency filter.

## Combining with Other Indicators

- **Regression Reversion** provides a percentage-based alternative to the absolute deviation measured here.
- **Z-Score Reversion** offers a normalized statistical view that can cross-confirm channel extremes.
- **RSI Divergence** adds momentum divergence confirmation at channel boundaries.
