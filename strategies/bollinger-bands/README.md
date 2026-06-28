# Bollinger Bands

The Bollinger Bands strategy is a classic mean-reversion system that buys when price touches the lower band and sells when price reaches the upper band. Created by John Bollinger, the bands consist of a simple moving average (basis) flanked by upper and lower envelopes set at a configurable number of standard deviations. This implementation is a streamlined long-only version: enter on lower band crosses and exit on upper band crosses, capturing the full band-to-band reversion move.

## Conceptual Diagram

```
Price
 │   · · · · Upper Band (MA + 2σ) · · · ·
 │  ·    ╱╲    ·         · ╱╲ ·
 │ ·    ╱  ╲    ·       ·╱  ╲ ·
 │·    ╱    ╲    ·     ·╱    ╲·
 │════╱══════╲════════╱════════╲══ Basis
 │  ╱         ╲      ╱         ╲
 │ ╱        ·  ╲    ╱·       ·  ╲
 │╱        ·    ╲  ╱· ·     ·    ╲
 │       ·  · · ·╲╱· · ·  · · · ·╲
 │      · · Lower Band (MA - 2σ) · ·
 └──────────────────────────────────── Time
   🟢 Cross above     🟢 Cross above
   lower band         lower band
            🔴 Cross below
            upper band = exit
```

## How It Works

The strategy calculates a simple moving average over the specified length (default 20), then adds and subtracts a multiple of the rolling standard deviation (default 2.0) to form the upper and lower bands. Under a normal distribution, roughly 95% of closing prices should fall within two standard deviations of the mean.

A long entry triggers when the closing price crosses above the lower band from below. This crossover indicates that price has been pushed to a statistical extreme on the downside and is beginning to recover. The strategy interprets this as a high-probability reversion setup where price is likely to move back toward the basis or beyond.

The long position is closed when price crosses below the upper band from above. This exit captures the full reversion move from the lower band to the upper band. Unlike the BB Bounce strategy, this implementation does not take short positions and does not offer a basis exit option, making it a simpler system focused on buying dips at statistical support levels.

The strategy is inherently contrarian: it buys weakness and sells strength. This works well in oscillating markets but can produce losses in strong downtrends where price repeatedly penetrates the lower band without reverting.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Length | 20 | 5-200 | Lookback period for the SMA and standard deviation calculation |
| Std Dev Multiplier | 2.0 | 0.5-5.0 | Number of standard deviations for band width |

## Python Advantage

The strategy achieves its complete logic in just a few lines by leveraging the `ta.bb()` function for vectorized band computation and tuple unpacking.

```python
# All three bands computed in a single vectorized call
upper, basis, lower = ta.bb(close, length, mult)

# Entry and exit with crossover detection on dynamic levels
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(close, upper)[-1]:
    strategy.close("Long")
```

The entire strategy logic fits in four executable lines after the band computation. The `ta.bb()` function internally computes the rolling mean and standard deviation across all bars simultaneously using numpy operations, making it dramatically faster than loop-based implementations. The `ta.crossover()` and `ta.crossunder()` functions handle the edge detection (previous bar below, current bar above) without manual state tracking.

## When to Use

Best for range-bound stocks, ETFs, and forex pairs on daily or 4-hour timeframes. The strategy thrives in markets that oscillate within a defined range over weeks or months. It is particularly effective on blue-chip stocks and index ETFs that tend to mean-revert after sharp pullbacks. Avoid during momentum-driven markets, breakout phases, or when a stock is in a sustained downtrend.

## Risk Management

Place a hard stop 1-2 ATR below the lower band at the time of entry to limit losses when the expected reversion fails. The standard deviation multiplier is the primary risk control: a 2.5 or 3.0 multiplier requires price to reach more extreme levels before entry, reducing false signals but also reducing trade frequency. Consider pairing with a trend filter to avoid buying lower band touches during strong downtrends where mean reversion is unlikely.

## Combining with Other Indicators

- **Choppiness Filter**: Confirm the market is range-bound (high choppiness) before trading band touches, avoiding trend periods where the strategy underperforms.
- **EMA Distance**: Use the EMA distance indicator to quantify how stretched price is from its average. Band touches combined with extreme EMA distance provide stronger reversion signals.
- **ADX Trend**: Filter out trades when ADX is above 30, ensuring the strategy only operates in non-trending environments where mean reversion has a statistical edge.
